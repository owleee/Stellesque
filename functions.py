import math
import pygame

def m(n):
    if abs(n) < 0.001:
        return 0
    return n


def cos(n):
    "returns the cosine value of a number entered in degrees"
    return math.cos(math.radians(n))


def sin(n):
    "returns the sine value of a number entered in degrees"
    return math.sin(math.radians(n))

def ssqrt(n):
  "safe sqrt: finds the sqrt of the abs of n"
  return math.sqrt(abs(n))


def centredRotate(image, angle, x, y):
    "rotates an image about its perfect centre"
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
      center = image.get_rect(
        center = (x,y)
      ).center
    )
    return rotated_image, new_rect

def sortZ(arr):
    for i in range(1, len(arr)):
        key = arr[i].z
        j = i-1
        while j >= 0 and key < arr[j].z :
                arr[j+1].z = arr[j].z
                j -= 1
        arr[j+1].z = key
