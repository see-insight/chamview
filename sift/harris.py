import os
from PIL import Image
from pylab import *
from scipy.ndimage import filters


'''
Compute the Harris corner detector response function for each pixel in a
graylevel image
'''
def compute_response(img,sigma=3):
    #derivatives
    imx = zeros(img.shape)
    filters.gaussian_filter(img,(sigma,sigma),(0,1),imx)
    imy = zeros(img.shape)
    filters.gaussian_filter(img,(sigma,sigma),(1,0),imy)

    #compute components of the Harris matrix
    Wxx = filters.gaussian_filter(imx*imx,sigma)
    Wxy = filters.gaussian_filter(imx*imy,sigma)
    Wyy = filters.gaussian_filter(imy*imy,sigma)

    #determinant and trace
    Wdet = Wxx*Wyy - Wxy**2
    Wtr = Wxx + Wyy
    return Wdet / Wtr


'''
Return corners from a Harris response image
-min_dist is the minimum number of pixels between corners and image boundary
-higher threshold means more corners
'''
def get_points(harrisim,min_dist=10,threshold=0.1):
    #find top corner candidates above a threshold
    corner_threshold = harrisim.max() * threshold
    harrisim_t = (harrisim > corner_threshold) * 1

    #get coordinates of candidates
    coords = array(harrisim_t.nonzero()).T
    #...and their values
    candidate_values = [harrisim[c[0],c[1]] for c in coords]
    #sort candidates
    index = argsort(candidate_values)

    #store allowed point locations in array
    allowed_locations = zeros(harrisim.shape)
    allowed_locations[min_dist:-min_dist,min_dist:-min_dist] = 1

    #select the best points taking min_distance into account
    filtered_coords = []
    for i in index:
        if allowed_locations[coords[i,0],coords[i,1]] == 1:
            filtered_coords.append(coords[i])
            allowed_locations[(coords[i,0]-min_dist):(coords[i,0]+min_dist),
                    (coords[i,1]-min_dist):(coords[i,1]+min_dist)] = 0
    return filtered_coords


'''
Plots corners found in an image
'''
def plot_points(image,filtered_coords):
    figure()
    gray()
    imshow(image)
    for p in filtered_coords:
        x = p[1]
        y = p[0]
        plot(x,y,'r*')
    axis('off')





