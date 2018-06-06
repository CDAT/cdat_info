"""
This script compares the png test image given in the second argument against
the known good baseline given in the third. Alternate known good images
(with _number.png in the filename) are also compared against.
"""

from __future__ import print_function
import math
import os
import sys
import logging
import shutil
try:
    import vtk
    hasVTK = True
except:
    hasVTK = False

defaultThreshold = 10.0


def image_compare(testImage, baselineImage):
    imageDiff = vtk.vtkImageDifference()
    imageDiff.SetInputData(testImage)
    imageDiff.SetImageData(baselineImage)
    imageDiff.Update()
    return (imageDiff.GetThresholdedError(), imageDiff.GetOutput())


def dump_image_to_file(fname, img):
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(fname)
    wr.SetInputData(img)
    wr.Write()


def image_from_file(fname):
    try:
        rd = vtk.vtkPNGReader()
        rd.SetFileName(fname)
        removeAlpha = vtk.vtkImageExtractComponents()
        removeAlpha.SetComponents(0, 1, 2)
        removeAlpha.SetInputConnection(rd.GetOutputPort())
        removeAlpha.Update()
        return removeAlpha.GetOutput()
    except Exception as err:
        print("Problem opening file '%s': %s" % (fname, err))
        return None


def find_alternates(fname):
    dirname = os.path.dirname(fname)
    prefix, ext = os.path.splitext(os.path.split(fname)[1])
    files = os.listdir(dirname)
    results = [fname]
    for i in files:
        if i.startswith(prefix) and i.endswith(ext) and i != prefix + ext:
            results.append(os.path.join(dirname, i))
    return results


def printDart(name, type, value, suff=""):
        print('<DartMeasurement%s name="%s" type="%s">%s</DartMeasurement%s>' % (
            suff, name, type, value, suff))


def check_result_image(fname, baselinefname, threshold=defaultThreshold,
                       baseline=True, cleanup=True, update_baseline=False):
                    
    if not hasVTK:
        print("Could not load VTK. Aborting image compare")
        return -1

    testImage = image_from_file(fname)
    if testImage is None:
        print("Testing image missing, test failed.")
        return -1

    if baseline:
        baselinefnames = find_alternates(baselinefname)
    else:
        baselinefnames = [baselinefname, ]

    print("Found Baselines:")
    for baselinefname in baselinefnames:
        print("- %s" % baselinefname)

    bestImage = None
    bestFilename = None
    bestDiff = None
    bestDiffImage = None
    for baselineFilename in baselinefnames:
        sys.stdout.write("Comparing %s %s ... " % (fname, baselineFilename))
        baselineImage = image_from_file(baselineFilename)
        if baselineImage is None:
            continue

        diff, diffImage = image_compare(testImage, baselineImage)

        sys.stdout.write("diff=%f" % diff)

        if bestDiff is None or diff < bestDiff:
            sys.stdout.write(", New best!")
            bestDiff = diff
            bestFilename = baselineFilename
            bestImage = baselineImage
            bestDiffImage = diffImage
            if bestDiff < threshold:
                break
        sys.stdout.write("\n")

    if bestImage is None:
        print("No baseline images found. Test failed.")
        return -1

    if update_baseline is True:
        print("UPDATE MODE updating %s with %s" % (bestFilename, fname))
        shutil.copy(fname, bestFilename)
        return 0

    if bestDiff < threshold:
        print(
            "Baseline '%s' is the best match with a difference of %f." %
            (bestFilename, bestDiff))
        if cleanup:
            print("Deleting test image '%s'..." % (fname))
            os.remove(fname)
        return 0

    print(
        "All baselines failed! Lowest error (%f) exceeds threshold (%f)." %
        (bestDiff, threshold))

    sp = fname.split(".")
    diffFilename = ".".join(sp[:-1]) + "_diff." + sp[-1]
    print("Saving image diff at %s" % diffFilename)
    dump_image_to_file(diffFilename, bestDiffImage)

    # Print metadata for CDash image upload:
    printDart("ImageError", "numeric/double", "%f" % bestDiff)
    printDart("TestImage", "image/png", os.path.abspath(fname), "File")
    printDart(
        "DifferenceImage",
        "image/png",
        os.path.abspath(diffFilename),
        "File")
    printDart("ValidImage", "image/png", os.path.abspath(bestFilename), "File")
    return -1

def checkImage(fnm, canvas, src=None, threshold=defaultThreshold,
                pngReady=False, pngPathSet=False, verbosity=1):
    if src is None:
        src = os.path.join(self.basedir, os.path.basename(fnm))
    if not pngPathSet:
        fnm = os.path.join(self.pngsdir, fnm)
    if verbosity>0:
        print("Test file  :", fnm)
        print("Source file:", src)
    if not pngReady:
        canvas.png(
            fnm,
            width=canvas.width,
            height=canvas.height,
            units="pixels")
    ret = check_result_image(fnm, src, threshold)
    return ret
