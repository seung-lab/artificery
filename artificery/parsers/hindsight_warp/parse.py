import torch
from scalenet import UpsampleResiduals
from scalenet.residuals import res_warp_img, combine_residuals

class HindsightWarp(torch.nn.Module):
    def __init__(self, rollback_range, inner_module):
        super().__init__()
        self.rollback_range = rollback_range
        self.inner_module = inner_module

    def forward(self, x, res, state, level):
        #Maybe this exit condition shouldn't be appplied to hindsight case
        if len(torch.nonzero(res))  == 0: #res is all 0's
            return x

        res = res.permute(0, 2, 3, 1)

        num_fms = x.shape[1]
        src = x[:, :num_fms//2]
        tgt = x[:, num_fms//2:]
        warped_tgt = res_warp_img(tgt, res, is_pix_res=True, rollback=self.rollback_range)
        res = res.permute(0, 3, 1, 2)

        in_bundle = torch.cat((src, tgt, warped_tgt, res), 1)

        hindsight_adjustment = self.inner_module(in_bundle)

        # this is aweful
        state['down'][str(level)]['input'] =  combine_residuals(res.permute(0, 2, 3, 1),
                                    hindsight_adjustment.permute(0, 2, 3, 1),
                                    rollback=self.rollback_range).permute(0, 3, 1, 2)

        res = state['down'][str(level)]['input'].permute(0, 2, 3, 1)
        hindsight_warped_tgt = res_warp_img(tgt, res, is_pix_res=True, rollback=self.rollback_range)
        result = torch.cat((src, hindsight_warped_tgt), 1)

        return result

def parse(params, create_module):
    rollback_range = params['arch_desc']['rollback']
    inner_module = create_module(params['arch_desc']['inner_module'])
    net = HindsightWarp(rollback_range, inner_module)
    return net
