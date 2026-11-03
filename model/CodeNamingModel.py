import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv


class CodeNamingModel(nn.Module):
    def __init__(self, encoder, decoder, config, beam_size, sos_id, eos_id, max_length, hidden_dim=512, ):
        super(CodeNamingModel, self).__init__()
        self.config = config
        self.encoder = encoder
        self.token_proj = nn.Linear(self.config.hidden_size, hidden_dim)
        self.gat1 = GATConv(hidden_dim, hidden_dim, heads=4)  
        self.gat2 = GATConv(hidden_dim * 4, hidden_dim, heads=4) 
        # self.fc = nn.Linear(hidden_dim * 4, self.config.hidden_size
        self.ffn = nn.Sequential(
            nn.Linear(hidden_dim * 4, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, self.config.hidden_size)
        )
        self.dense = nn.Linear(self.config.hidden_size, self.config.hidden_size)
        self.lm_head = nn.Linear(self.config.hidden_size, self.config.vocab_size, bias=False)
        # Attention Pooling
        self.att_pooling = nn.Sequential(
            nn.Linear(self.config.hidden_size, self.config.hidden_size),
            nn.Tanh(),
            nn.Linear(self.config.hidden_size, 1)
        )
        self.decoder = decoder
        self.lsm = nn.LogSoftmax(dim=-1)
        self.register_buffer("bias", torch.tril(torch.ones(2048, 2048)))
        self.beam_size = beam_size
        self.sos_id = sos_id
        self.eos_id = eos_id
        self.max_length = max_length
    
    def forward(self, input_ids, attention_mask, edge_index, decoder_input_ids=None, decoder_attention_mask=None, args=None):
        batch_size, node_len, seq_len = input_ids.shape
        num_edges = edge_index[0].shape[1] 

        all_input_ids_cat = input_ids.view(-1, seq_len)         # [batch_size * node_len, seq_len]
        all_attention_mask_cat = attention_mask.view(-1, seq_len)

        encoder_outputs = self.encoder(
            input_ids=all_input_ids_cat,
            attention_mask=all_attention_mask_cat,
        )
        token_embeddings = encoder_outputs.last_hidden_state[:, 0, :]  # [B*N, hidden_dim]

        node_features = self.token_proj(token_embeddings)  # [B*N, hidden_dim]

        all_edge_index = []
        for i in range(batch_size):
            node_offset = i * node_len
            edge_index_i = edge_index[i] + node_offset  
            all_edge_index.append(edge_index_i)

        edge_index_cat = torch.cat(all_edge_index, dim=1)  # [2, B*num_edges]

        x = F.relu(self.gat1(node_features, edge_index_cat))
        x = F.relu(self.gat2(x, edge_index_cat))
        # x = [B*N, enc_hidden_dim]
        x = self.ffn(x) 
        # batch = [B*N]
        batch = torch.arange(batch_size, device=x.device).repeat_interleave(node_len)
        # graph_summary = [batch_size, enc_hidden_dim]
        graph_summary = self.attention_pooling(x, batch)
        # encoder_output = [1, batch_size, enc_hidden_dim]
        encoder_output = graph_summary.unsqueeze(1).permute([1,0,2]).contiguous()
        if decoder_input_ids is not None:
            attn_mask=-1e4 *(1-self.bias[:decoder_input_ids.shape[1],:decoder_input_ids.shape[1]])
            tgt_embeddings = self.encoder.embeddings(decoder_input_ids).permute([1,0,2]).contiguous()
            out = self.decoder(tgt_embeddings,encoder_output,tgt_mask=attn_mask)
            hidden_states = torch.tanh(self.dense(out)).permute([1,0,2]).contiguous()
            lm_logits = self.lm_head(hidden_states)
            # Shift so that tokens < n predict n
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = decoder_input_ids[..., 1:].contiguous()
            # Flatten the tokens
            loss_fct = nn.CrossEntropyLoss(ignore_index=-1)
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)),
                            shift_labels.view(-1))
            return lm_logits, loss
        else:
            #Predict 
            preds=[]       
            zero=torch.cuda.LongTensor(1).fill_(0)     
            for i in range(input_ids.shape[0]):
                context=encoder_output[:,i:i+1]
                beam = Beam(self.beam_size,self.sos_id,self.eos_id)
                cur_ids=beam.getCurrentState()
                context=context.repeat(1, self.beam_size,1)
                for _ in range(self.max_length): 
                    if beam.done():
                        break
                    attn_mask=-1e4 *(1-self.bias[:cur_ids.shape[1],:cur_ids.shape[1]])
                    tgt_embeddings = self.encoder.embeddings(cur_ids).permute([1,0,2]).contiguous()
                    # context = [1, beam_size, enc_hidden_dim]
                    # tgt_embeddings = [seq_len, beam_size, hidden_dim]
                    out = self.decoder(tgt_embeddings,context,tgt_mask=attn_mask)
                    out = torch.tanh(self.dense(out))
                    hidden_states=out.permute([1,0,2]).contiguous()[:,-1,:]
                    out = self.lsm(self.lm_head(hidden_states)).data
                    beam.advance(out)
                    cur_ids.data.copy_(cur_ids.data.index_select(0, beam.getCurrentOrigin()))
                    cur_ids=torch.cat((cur_ids,beam.getCurrentState()),-1)
                hyp= beam.getHyp(beam.getFinal())
                pred=beam.buildTargetTokens(hyp)[:self.beam_size]
                pred=[torch.cat([x.view(-1) for x in p]+[zero]*(self.max_length-len(p))).view(1,-1) for p in pred]
                preds.append(torch.cat(pred,0).unsqueeze(0))
                
            preds=torch.cat(preds,0)              
            return preds


    def attention_pooling(self, x, batch):
        # scores = [B*N]
        scores = self.att_pooling(x).squeeze(-1)  
        scores = torch.exp(scores)
        segment_sum = torch.zeros(batch.max().item() + 1, device=x.device).scatter_add_(0, batch, scores)
        scores = scores / (segment_sum[batch] + 1e-6)
        # x_weighted = [B*N, hidden_dim * 4]
        x_weighted = x * scores.unsqueeze(-1)  
        # out = [batch_size, hidden_dim * 4]
        out = torch.zeros(batch.max().item() + 1, x.size(1), device=x.device).scatter_add_(0, batch.unsqueeze(-1).expand_as(x), x_weighted)
        return out
    
class Beam(object):
    def __init__(self, size,sos,eos):
        self.size = size
        self.tt = torch.cuda
        # The score for each translation on the beam.
        self.scores = self.tt.FloatTensor(size).zero_()
        # The backpointers at each time-step.
        self.prevKs = []
        # The outputs at each time-step.
        self.nextYs = [self.tt.LongTensor(size)
                       .fill_(0)]
        self.nextYs[0][0] = sos
        # Has EOS topped the beam yet.
        self._eos = eos
        self.eosTop = False
        # Time and k pair for finished.
        self.finished = []

    def getCurrentState(self):
        "Get the outputs for the current timestep."
        batch = self.tt.LongTensor(self.nextYs[-1]).view(-1, 1)
        return batch

    def getCurrentOrigin(self):
        "Get the backpointers for the current timestep."
        return self.prevKs[-1]

    def advance(self, wordLk):
        """
        Given prob over words for every last beam `wordLk` and attention
        `attnOut`: Compute and update the beam search.

        Parameters:

        * `wordLk`- probs of advancing from the last step (K x words)
        * `attnOut`- attention at the last step

        Returns: True if beam search is complete.
        """
        numWords = wordLk.size(1)
        # Sum the previous scores.
        if len(self.prevKs) > 0:
            beamLk = wordLk + self.scores.unsqueeze(1).expand_as(wordLk)

            # Don't let EOS have children.
            for i in range(self.nextYs[-1].size(0)):
                if self.nextYs[-1][i] == self._eos:
                    beamLk[i] = -1e20
        else:
            beamLk = wordLk[0]
        flatBeamLk = beamLk.view(-1)
        bestScores, bestScoresId = flatBeamLk.topk(self.size, 0, True, True)

        self.scores = bestScores

        # bestScoresId is flattened beam x word array, so calculate which
        # word and beam each score came from
        prevK = bestScoresId // numWords
        self.prevKs.append(prevK)
        self.nextYs.append((bestScoresId - prevK * numWords))


        for i in range(self.nextYs[-1].size(0)):
            if self.nextYs[-1][i] == self._eos:
                s = self.scores[i]
                self.finished.append((s, len(self.nextYs) - 1, i))

        # End condition is when top-of-beam is EOS and no global score.
        if self.nextYs[-1][0] == self._eos:
            self.eosTop = True

    def done(self):
        return self.eosTop and len(self.finished) >=self.size

    def getFinal(self):
        if len(self.finished) == 0:
            self.finished.append((self.scores[0], len(self.nextYs) - 1, 0))
        self.finished.sort(key=lambda a: -a[0])
        if len(self.finished) != self.size:
            unfinished=[]
            for i in range(self.nextYs[-1].size(0)):
                if self.nextYs[-1][i] != self._eos:
                    s = self.scores[i]
                    unfinished.append((s, len(self.nextYs) - 1, i)) 
            unfinished.sort(key=lambda a: -a[0])
            self.finished+=unfinished[:self.size-len(self.finished)]
        return self.finished[:self.size]

    def getHyp(self, beam_res):
        """
        Walk back to construct the full hypothesis.
        """
        hyps=[]
        for _,timestep, k in beam_res:
            hyp = []
            for j in range(len(self.prevKs[:timestep]) - 1, -1, -1):
                hyp.append(self.nextYs[j+1][k])
                k = self.prevKs[j][k]
            hyps.append(hyp[::-1])
        return hyps
    
    def buildTargetTokens(self, preds):
        sentence=[]
        for pred in preds:
            tokens = []
            for tok in pred:
                if tok==self._eos:
                    break
                tokens.append(tok)
            sentence.append(tokens)
        return sentence

