# regOct
an implementation of an ordered octree system

## Design principles
0. Provide an effective, comprehensive storage medium for cubic, three-dimensional data.
1. The order in which the commands are stored in the file imply the position at which they are executed.
2. State checks within the octree are linear and processor unintensive.
3. The Octree is a self-contained system. All information regarding the octree is stored in the file.



# Use
## 1. General use
Every octree has an integer "level", which defines its size. For a given level, the octree takes the form of a cube with ranges of 0 - 2**level.
```python 
regoct.Octree(level) -> Octree

# setting a value:
octree[(x, y, z, level)] = new_value
# level may be omitted if it is 0:
octree[(x, y, z)] = new_value

# getting a value:
value = octree[(x, y, z)]
```

## 2. Basic octree IO
In case it is necessary to preserve an octree for later use, it may be saved and loaded to the filesystem via as shown below:
```python
import regoct

original_octree = Octree(2)
# load information into octree

file_path = "file_path.onc"
regoct.save(octree, file_path)
loaded_octree = regoct.load(file_path)

assert original_octree == loaded_octree
```
This however has a major caveat: the octrees serialized this way may only have internal values of python's base data types:
```python
None(wip), Ellipsis(wip), bool(wip), int, float, complex, str, list, dict, set 
```
This is addressed followingly.
## 3. Advanced octree IO

regoct provides a API to modify the serialization process. This is useful for implementing routines for class instances.

The ABC regoct.Interface supplies the tools for implementing the API. It requires the methods `to_file(obj, saver: "regoct.SavingStream")` and `from_file(cls, loader: "regoct.LoadingStream")`, where the params **saver** and **loader** provide access to the data using a set of methods. These methods in loader and saver mirror each other and are as follows:
regoct.SavingStream | regoct.LoadingStream | description
-|-|-
saver.convert(value) | loader.convert() -> any | dynamic conversion
saver.i8(value) | loader.i8() -> int | 8-bit signed integer
saver.i16(value) | loader.i16() -> int | 16-bit signed integer
saver.i32(value) | loader.i32() -> int | 32-bit signed integer
saver.i64(value) | loader.i64() -> int | 64-bit signed integer
saver.u8(value) | loader.u8() -> int | 8-bit unsigned integer
saver.u16(value) | loader.u16() -> int | 16-bit unsigned integer
saver.u32(value) | loader.u32() -> int | 32-bit unsigned integer
saver.u64(value) | loader.u64() -> int | 64-bit unsigned integer
saver.f32(value) | loader.f32() -> float | 32-bit float
saver.f64(value) | loader.f64() -> float | 64-bit float
saver.c64(value) | loader.c64() -> complex | 2x 32-bit float complex number
saver.c128(value) | loader.c128() -> complex | 2x 64-bit float complex number
saver.Str(value) | loader.Str() -> str | variable-length utf-8 string
saver.List(value) | loader.List() -> list | variable-length dynamic-type list
saver.Dict(value) | loader.Dict() -> dict | variable-length dynamic-type dict
saver.Set(value) | loader.Set() -> set | variable-length dynamic-type set

Be aware that the order in which these methods are called in the to_file and from_file methods should be equal to eachother.

```python 
import regoct
from regoct import Interface, SavingStream, LoadingStream

class DataPacket(Interface):
    def __init__(self, *args, **kwds):...

    def to_file(obj, saver: SavingStream):...

    def from_file(cls, loader: LoadingStream):...


original_octree = regoct.Octree(2)
# load information into octree

file_path = "file_path.onc"
DataPacket.save(octree, file_path)
loaded_octree = DataPacket.load(file_path)

assert original_octree == loaded_octree
``` 

## Visualisation:
The module has an interactable viewer to render octrees in 3d. 
Currently, this is done with the statement `regoct.Display(octree).main()`, but since this is very verbose, expect it to change.


## And now for something completely different
![**no one expects the spanish inquisition**](https://static.wikia.nocookie.net/montypython/images/f/ff/Spanish_Inquisition.jpg/revision/latest?cb=20180629171423)
