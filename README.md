# regOct
an implementation of an ordered octree system

## Design principles
0. Provide an effective, comprehensive storage medium for cubic, three-dimensional data.
1. The order in which the commands are stored in the file imply the position at which they are executed.
2. State checks within the octree are linear and processor unintensive.
3. The Octree is a self-contained system. All information regarding the octree is stored in the file.

## File Format (.onc)
The **.onc** format (octree encrypted code) is the file format of choice for this code. In its current state (**v. 0.2.0**) data is stored as standard text and, as such, can be read, understood and written by regular mortals. 

### Important Notice:
1. As regOct, and its data format, store raw values (currently strings), it is a highly abstracted data format. What the values represent is entirely dependant on the software interpreting it, so caution must be applied when loading a file. This also means that a program can have two seperate and unique regOct instances, where the same values are used differently. As such, a regOct instance **MUST** be bound to an enum.
2. All theoretical points in regOct are equidistant. If, for whatever reason, complex 3d data must be stored, then that must be done so as an attribute. This is because the highly ordered nature of the format allows for high-speed get()-calls (the get() code is ridiculously short).

## Visualisation
Integrated with the package <del>is</del> :trollface: will be a handy-dandy pyGame-based octree visualiser, that utilises state-of-the-art rect() calls.