# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 23:07:34 2021

@author: Bruno Caneco

Code stolen from package in https://github.com/jobevers/diagonal-crop. Package was
converted into a single module to simplify integration with sscd's code structure


TODO

"""

from __future__ import division

import collections
import math


_Point = collections.namedtuple('Point', ['x', 'y'])


class Point(_Point):
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def recenter(self, old_center, new_center):
        return self + (new_center - old_center)

    # http://homepages.inf.ed.ac.uk/rbf/HIPR2/rotate.htm
    def rotate(self, center, angle):
        # angle should be in radians
        x = math.cos(angle) * (self.x - center.x) - math.sin(angle) * (self.y - center.y) + center.x
        y = math.sin(angle) * (self.x - center.x) + math.cos(angle) * (self.y - center.y) + center.y
        return Point(x, y)



def getCenter(im):
    return Point(*(d / 2 for d in im.size))


Bound = collections.namedtuple('Bound', ('left', 'upper', 'right', 'lower'))


def getBounds(points):
    xs, ys = zip(*points)
    # left, upper, right, lower using the usual image coordinate system
    # where top-left of the image is 0, 0
    return Bound(min(xs), min(ys), max(xs), max(ys))


def getBoundsCenter(bounds):
    return Point(
        (bounds.right - bounds.left) / 2 + bounds.left,
        (bounds.lower - bounds.upper) / 2 + bounds.upper
    )


def roundint(values):
    return tuple(int(round(v)) for v in values)


def getRotatedRectanglePoints(angle, base_point, height, width):
    # base_point is the upper left (ul)
    ur = Point(
        width * math.cos(angle),
        -width * math.sin(angle)
    )
    lr = Point(
        ur.x + height * math.sin(angle),
        ur.y + height * math.cos(angle)
    )
    ll = Point(
        height * math.cos(math.pi / 2 - angle),
        height * math.sin(math.pi / 2 - angle)
    )
    return tuple(base_point + pt for pt in (Point(0, 0), ur, lr, ll))



def crop(im, base, angle, height, width):
    """Return a new, cropped image.

    Args:
        im: a PIL.Image instance
        base: a (x,y) tuple for the upper left point of the cropped area
        angle: angle, in radians, for which the cropped area should be rotated
        height: height in pixels of cropped area
        width: width in pixels of cropped area
    """
    base = Point(*base)
    points = getRotatedRectanglePoints(angle, base, height, width)
    return _cropWithPoints(im, angle, points)


def _cropWithPoints(im, angle, points):
    bounds = getBounds(points)
    im2 = im.crop(roundint(bounds))
    bound_center = getBoundsCenter(bounds)
    crop_center = getCenter(im2)
    # in the cropped image, this is where our points are
    crop_points = [pt.recenter(bound_center, crop_center) for pt in points]
    # this is where the rotated points would end up without expansion
    rotated_points = [pt.rotate(crop_center, angle) for pt in crop_points]
    # expand is necessary so that we don't lose any part of the picture
    im3 = im2.rotate(-angle * 180 / math.pi, expand=True)
    # but, since the image has been expanded, we need to recenter
    im3_center = getCenter(im3)
    rotated_expanded_points = [pt.recenter(crop_center, im3_center) for pt in rotated_points]
    im4 = im3.crop(roundint(getBounds(rotated_expanded_points)))
    return im4





