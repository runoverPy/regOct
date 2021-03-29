# regOct
an implementation of an ordered octree system

## Design principles
0. Provide an effective, comprehensive storage medium for cubic, three-dimensional data.
1. The order in which the commands are stored in the file imply the position at which they are executed.
2. State checks within the octree are linear and processor unintensive.
3. The Octree is a self-contained system. All information regarding the octree is stored in the file.

## File Format (.onc)
The **.onc** (octree encrypted code) format is the file format of choice for this code. In its current state data is stored as plain text and, as such, can be read, understood and written by regular mortals. This is soon to change, it will soon be stored in binary.

### Important Notices:
1. Because the value contained in the octree is type-independant, what it represents is entirely dependant on the software interpreting it, so caution must be applied when loading a file.
2. Points on the octree don't naturally store their coordinates, only where they are relative to the node above. These are automatically generated when calling map(), and are integers. If, for whatever reason, complex 3d data must be stored, then that must be done so as an attribute.

## Visualisation:
The module has an interactable viewer to render octrees in 3d. 


## And now for something completely different
![**no one expects the spanish inquisition**](https://static.wikia.nocookie.net/montypython/images/f/ff/Spanish_Inquisition.jpg/revision/latest?cb=20180629171423)
