from numpy import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from skimage.feature import match_template
import skimage.color as color
from PIL import ImageEnhance
#from skimage import exposure

def test(image, coin):
    result = match_template(image, coin)
    ij = unravel_index(argmax(result), result.shape)
    x, y = ij[::-1]
    
    '''fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(8, 3))

    ax1.imshow(coin)
    ax1.set_axis_off()
    ax1.set_title('template')

    ax2.imshow(image)
    ax2.set_axis_off()
    ax2.set_title('image')
    # highlight matched region
    hcoin, wcoin = coin.shape
    rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
    ax2.add_patch(rect)

    ax3.imshow(result)
    ax3.set_axis_off()
    ax3.set_title('`match_template`\nresult')
    # highlight matched region
    ax3.autoscale(False)
    ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

    plt.show()'''
    
    return y,x

def confidence(count, templates, curr_slice):

    tmp_sum = 0
    r = templates[count][0]
    c = templates[count][2]
    
    while r >= templates[count][0] and r < templates[count][1]:
        c = templates[count][2]
        while c >= templates[count][2] and c < templates[count][3]:
            tmp_sum += curr_slice[r][c]
            c+=1
        r+=1
    tmp_avg = float(tmp_sum)/((templates[count][1]-templates[count][0])*
                              (templates[count][3]-templates[count][2]))
    
    dev_sum = 0
    r = templates[count][0]
    
    while r >= templates[count][0] and r < templates[count][1]:
        c = templates[count][2]      
        while c >= templates[count][2] and c < templates[count][3]:
            dev_sum += abs(curr_slice[r][c]-tmp_avg)
            c+=1
        r+=1
    std_dev = dev_sum/((templates[count][1]-templates[count][0])*
                       (templates[count][3]-templates[count][2]))
    return 100-std_dev   

def colorspace(image):

    pil_im = Image.open(image)
    
    enhancer = ImageEnhance.Contrast(pil_im)
    im_enh = enhancer.enhance(2)
    
    rgb = mpimg.pil_to_array(pil_im)
    hsv = color.rgb2hsv(rgb)
    xyz = color.rgb2xyz(rgb)
    grey = color.rgb2grey(rgb)
    cie = color.rgb2rgbcie(rgb)
    enh = mpimg.pil_to_array(im_enh)

    r,c = rgb[:,:,0].shape

    slices = [rgb[:,:,0], rgb[:,:,1], rgb[:,:,2],
              hsv[:,:,0], hsv[:,:,1], hsv[:,:,2],
              grey,
              enh[:,:,0], enh[:,:,1], enh[:,:,2],
              cie[:,:,0], cie[:,:,1], cie[:,:,2],
              xyz[:,:,0], xyz[:,:,1]]#, xyz[:,:,2]]

    dist_compare = [[int(r*3/40),int(r*12/40),
                     int(c*6/40),int(c*19/40)],
                    [int(r*3/40),int(r*7/40),
                     int(c*18/40),int(c*22/40)],
                    [int(r*4/40),int(r*9/40),
                     int(c*24/40),int(c*35/40)],
                    [int(r*9/40),int(r*12/40),
                     int(c*33/40),int(c*35/40)],
                    [int(r*19/40),int(r*23/40),
                     int(c*12/40),int(c*17/40)],
                    [int(r*18/40),int(r*25/40),
                     int(c*22/40),int(c*27/40)],
                    [int(r*16/40),int(r*20/40),
                     int(c*35/40),int(c*39/40)],
                    [int(r*28/40),int(r*38/40),
                     int(c*4/40),int(c*19/40)],
                    [int(r*25/40),int(r*32/40),
                     int(c*31/40),int(c*37/40)],
                    [int(r*34/40),int(r*38/40),
                     int(c*25/40),int(c*31/40)]]

    color_list = ['red','green','blue','hue','saturation','value',
                 'grey','enh red','enh green', 'enh blue',
                 'r cie','g cie', 'b cie','x','y','z']  
       
    slice_count = 0
    errors = []
 
    while slice_count < len(slices):
        temp_count = 0
        err_dist = 0
        curr_im = slices[slice_count]
        
        templates = [curr_im[int(r*3/40):int(r*12/40),
                             int(c*6/40):int(c*19/40)],
                     curr_im[int(r*3/40):int(r*7/40),
                             int(c*18/40):int(c*22/40)],
                     curr_im[int(r*4/40):int(r*9/40),
                             int(c*24/40):int(c*35/40)],
                     curr_im[int(r*9/40):int(r*12/40),
                             int(c*33/40):int(c*35/40)],
                     curr_im[int(r*19/40):int(r*23/40),
                             int(c*12/40):int(c*17/40)],
                     curr_im[int(r*18/40):int(r*25/40),
                             int(c*22/40):int(c*27/40)],
                     curr_im[int(r*16/40):int(r*20/40),
                             int(c*35/40):int(c*39/40)],
                     curr_im[int(r*28/40):int(r*38/40),
                             int(c*4/40):int(c*19/40)],
                     curr_im[int(r*25/40):int(r*32/40),
                             int(c*31/40):int(c*37/40)],
                     curr_im[int(r*34/40):int(r*38/40),
                             int(c*25/40):int(c*31/40)]]
        
        while temp_count < len(templates):
            row,col = test(slices[slice_count],templates[temp_count])
            err_dist += sqrt((row-dist_compare[temp_count][0])**2+
                             (col-dist_compare[temp_count][2])**2)
            print 'confidence: ', confidence(temp_count, dist_compare,
                                             slices[slice_count])
            print 'distance: ', sqrt((row-dist_compare[temp_count][0])**2+
                                     (col-dist_compare[temp_count][2])**2)
            temp_count += 1
        errors.append(err_dist)
        slice_count += 1
    least_item = errors[0]
    least_ind = 0
    for index,item in enumerate(errors):   
        if item < least_item:
            least_item = item
            least_ind = index
    #print error_list
    return color_list[least_ind]

print colorspace('test_file')
