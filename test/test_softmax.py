import torch
import time
import numpy as np
import torch.nn.functional as F
# 添加上一层目录到模块搜索路径
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 现在可以导入 softmaxCuda
import softmaxCuda

device = 'cuda' if torch.cuda.is_available() else 'cpu'
ndim = 3
test_shape = [700, 1200, 24]  
test_axis = ndim - 1
dimsize = test_shape[test_axis]
size = 1
stride = 1
for i in range(ndim - 1, -1, -1):
    size *= test_shape[i]
for i in range(ndim - 1, -1, -1):
    
    if(test_axis == i):
        break
    stride *= test_shape[i]


Q = torch.randn(test_shape, device=device, dtype=torch.float32, requires_grad=False) 

repeat = 20
#下面开始预热
for i in range(repeat):
    soTorch = torch.softmax(Q, axis = test_axis)
#正式计时
start_time = time.time()
for i in range(repeat):
    soTorch = torch.softmax(Q, axis = test_axis)
torch_softmax_time = 1000 * (time.time() - start_time)
print("PyTorch softmax time: %.6f ms"%(torch_softmax_time / repeat))





Q_output = torch.zeros(test_shape, device=device, dtype=torch.float32) 
#下面开始预热
for i in range(repeat):
    softmaxCuda.softmax(Q, Q_output, size, dimsize, stride)
#正式计时
start_time = time.time()
for i in range(repeat):
    softmaxCuda.softmax(Q, Q_output, size, dimsize, stride)
custom_softmax_time = 1000 * (time.time() - start_time)
print("Cuda core Softmax time: %.6f ms"%(custom_softmax_time / repeat))

# 将结果转换回 PyTorch 张量以进行比较
tmpa = soTorch.to('cpu').reshape(-1,1).numpy().flatten()

tmpb = Q_output.to('cpu').reshape(-1,1).numpy().flatten()

print(tmpa.shape, type(tmpa), tmpb.shape, type(tmpb))
atol = max(abs(tmpa - tmpb))

rtol = atol / max(abs(tmpb) + 1e-8)


print("absolute error:%.4e"%(atol))
print("relative error:%.4e"%(rtol))

# 对比性能
speedup = torch_softmax_time / custom_softmax_time
print(f"Speedup of Custom Tensor Core Softmax over PyTorch Softmax: {speedup:.2f}x")
