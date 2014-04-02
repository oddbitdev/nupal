nupal
=====

open source Python implementation of a program that I wrote some years ago for a furniture company, with the aim to reduce waste when cutting wooden sheets, by running an algorithm for optimal positioning. Little did I know at that time that this would be kind of NP-hard, in the end I settled for a recursive algorithm that tried to fit pieces of wood to be cut on the large sheet by subdividing the remaining space after placing one piece and so forth until no more pieces could fit on a sheet.

This implementation uses PySide for the interface and Pygame for running the solution algorithm for random samples, it's about halfway done, and if you want to run it you will need both mentioned libraries for Python 2.7
