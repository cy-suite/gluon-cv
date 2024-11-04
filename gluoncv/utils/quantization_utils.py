import mxnet as mx
def quantize_model(symbol, params, ctx=mx.cpu()):
    quantized_sym, quantized_params = mx.contrib.quant._quantize_symbol(symbol, params)
    return quantized_sym, quantized_params
