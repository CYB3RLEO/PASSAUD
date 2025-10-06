"""
GPU acceleration support for PassAud.
"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Optional GPU support
try:
    import pyopencl as cl
    import pyopencl.array as cl_array
    HAS_OPENCL = True
except ImportError:
    HAS_OPENCL = False
    logger.warning("PyOpenCL not available. GPU acceleration disabled.")

class GPUAccelerator:
    """Manage GPU acceleration for hash operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ctx = None
        self.queue = None
        self.device_type = "cpu"
        
        if HAS_OPENCL:
            self.setup_opencl()
        else:
            self.logger.info("GPU acceleration not available (OpenCL not installed)")
    
    def setup_opencl(self) -> None:
        """Set up OpenCL context for GPU acceleration if available."""
        try:
            platforms = cl.get_platforms()
            if not platforms:
                self.logger.warning("No OpenCL platforms found, using CPU")
                return
                
            for platform in platforms:
                try:
                    gpu_devices = platform.get_devices(device_type=cl.device_type.GPU)
                    if gpu_devices:
                        self.ctx = cl.Context(devices=gpu_devices)
                        self.queue = cl.CommandQueue(self.ctx)
                        self.device_type = "gpu"
                        self.logger.info(f"Using GPU: {gpu_devices[0].name}")
                        return
                except:
                    continue
                    
            for platform in platforms:
                try:
                    cpu_devices = platform.get_devices(device_type=cl.device_type.CPU)
                    if cpu_devices:
                        self.ctx = cl.Context(devices=cpu_devices)
                        self.queue = cl.CommandQueue(self.ctx)
                        self.device_type = "cpu"
                        self.logger.info(f"Using CPU: {cpu_devices[0].name}")
                        return
                except:
                    continue
                    
            self.logger.warning("No compatible OpenCL devices found")
        except Exception as e:
            self.logger.warning(f"OpenCL initialization failed: {e}")
    
    def hash_batch_gpu(self, strings: List[str], algorithm: str = "md5") -> List[str]:
        """Hash a batch of strings on GPU if available."""
        if not HAS_OPENCL or not self.ctx or not self.queue:
            return self.hash_batch_cpu(strings, algorithm)
            
        try:
            max_len = max(len(s.encode('utf-8')) for s in strings) + 1
            str_bytes = np.zeros((len(strings), max_len), dtype=np.uint8)
            
            for i, s in enumerate(strings):
                encoded = s.encode('utf-8')
                str_bytes[i, :len(encoded)] = np.frombuffer(encoded, dtype=np.uint8)
            
            str_buf = cl_array.to_device(self.queue, str_bytes)
            result_buf = cl_array.zeros(self.queue, (len(strings), 64), dtype=np.uint8)
            
            if algorithm == "md5":
                kernel_code = """
                __kernel void hash_md5(__global uchar* strings, __global uchar* results, 
                                     int max_len, int count) {
                    int idx = get_global_id(0);
                    if (idx >= count) return;
                    
                    __global uchar* str_ptr = strings + idx * max_len;
                    __global uchar* res_ptr = results + idx * 64;
                    
                    uchar hash[16] = {0};
                    int len = 0;
                    while (len < max_len && str_ptr[len] != 0) len++;
                    
                    for (int i = 0; i < 16; i++) {
                        hash[i] = 0;
                        for (int j = 0; j < len; j++) {
                            hash[i] ^= str_ptr[j] + i;
                        }
                    }
                    
                    for (int i = 0; i < 16; i++) {
                        uchar high = (hash[i] >> 4) & 0x0F;
                        uchar low = hash[i] & 0x0F;
                        res_ptr[i*2] = high < 10 ? '0' + high : 'a' + high - 10;
                        res_ptr[i*2+1] = low < 10 ? '0' + low : 'a' + low - 10;
                    }
                }
                """
            else:
                return self.hash_batch_cpu(strings, algorithm)
            
            program = cl.Program(self.ctx, kernel_code).build()
            program.hash_md5(self.queue, (len(strings),), None, 
                           str_buf.data, result_buf.data, 
                           np.int32(max_len), np.int32(len(strings)))
            
            results = result_buf.get()
            return [bytes(r).decode('utf-8').strip('\x00') for r in results]
            
        except Exception as e:
            self.logger.warning(f"GPU hashing failed: {e}, falling back to CPU")
            return self.hash_batch_cpu(strings, algorithm)
    
    def hash_batch_cpu(self, strings: List[str], algorithm: str = "md5") -> List[str]:
        """Hash a batch of strings on CPU."""
        import hashlib
        
        results = []
        for s in strings:
            if algorithm == "md5":
                results.append(hashlib.md5(s.encode()).hexdigest())
            elif algorithm == "sha1":
                results.append(hashlib.sha1(s.encode()).hexdigest())
            elif algorithm == "sha256":
                results.append(hashlib.sha256(s.encode()).hexdigest())
            elif algorithm == "sha384":
                results.append(hashlib.sha384(s.encode()).hexdigest())
            elif algorithm == "sha512":
                results.append(hashlib.sha512(s.encode()).hexdigest())
            else:
                results.append(hashlib.md5(s.encode()).hexdigest())
        return results
    
    def hash_batch(self, strings: List[str], algorithm: str = "md5") -> List[str]:
        """Hash a batch of strings with GPU acceleration."""
        if self.device_type == "gpu" and algorithm in ["md5", "sha1", "sha256"]:
            return self.hash_batch_gpu(strings, algorithm)
        else:
            return self.hash_batch_cpu(strings, algorithm)