# regOct
an implementation of an ordered octree system

## Design principles
1. The order in which the commands are stored in the file imply the position at which they are executed.
2. State checks within the octree are linear and processor unintensive.
3. The Octree is a self-contained system. All information regarding the octree is stored in the file.

## File Format (.onc)
The **.onc** format (octree encrypted code) is the file format of choice for this code. In its current state (**v. 0.2.0**) data is stored as standard text and, as such, can be read, understood and written by regular mortals. 
