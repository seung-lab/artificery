from scalenet import Sequence

def parse(params, create_module):
    batchnorm = True
    if 'batchnorm' in params and not params['batchnorm']:
        batchnorm = False
    net = Sequence(params["arch_desc"], batchnorm=batchnorm)
    return net
