import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from colormath.color_objects import LabColor, sRGBColor, LuvColor, LCHabColor, LCHuvColor, HSLColor
from colormath.color_conversions import convert_color


def CIELCHab_to_rgb(l, c, h):
        lab = LCHabColor(lch_l=l, lch_c=c, lch_h=h)
        rgb = convert_color(lab, sRGBColor)
        rgb_values = (rgb.rgb_r, rgb.rgb_g, rgb.rgb_b)


        max_value = max(rgb_values)

        if max_value > 1.0:
            rgb_values = tuple(min(value, 1) for value in rgb_values)
        return rgb_values

def CIELCHuv_to_rgb(l, c, h):
        lab = LCHuvColor(lch_l=l, lch_c=c, lch_h=h)
        rgb = convert_color(lab, sRGBColor)
        rgb_values = (rgb.rgb_r, rgb.rgb_g, rgb.rgb_b)


        max_value = max(rgb_values)

        if max_value > 1.0:
            rgb_values = tuple(min(value, 1) for value in rgb_values)
        return rgb_values

def HSL_to_rgb(h, s, l):
     hsl = HSLColor(h, s, l)
     rgb = convert_color(hsl, sRGBColor)
     rgb_values = (rgb.rgb_r, rgb.rgb_g, rgb.rgb_b)

     return rgb_values
      
for L in [0, 50, 100]:
    # Create a color wheel for CIELCHab
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    hue_samples = 360  

    # Define a range of chroma values (radii)
    chroma_range = np.linspace(0, 120, num=6) 

    for chroma in chroma_range:
        # Create an array of hue angles and their corresponding RGB colors
        hue_angles = np.radians(np.linspace(0, 360, hue_samples))
        colors = [CIELCHab_to_rgb(L, chroma, h) for h in np.linspace(0, 360, hue_samples)]

        # Plot each color segment at the given chroma (radius)
        for angle, color in zip(hue_angles, colors):
            ax.bar(angle, chroma, width=hue_angles[1] - hue_angles[0], color=color, edgecolor=color)

    ax.set_ylim(0, np.max(chroma_range))

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    ax.set_title('CIELCHab Color Wheel at L* = ' + str(L))

    name = "lchab_L_" + str(L) + ".png"
    plt.savefig(name)
    plt.show()

    # Create a color wheel for CIELCHuv
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    hue_samples = 360  

    chroma_range = np.linspace(0, 120, num=6) 

    for chroma in chroma_range:
        hue_angles = np.radians(np.linspace(0, 360, hue_samples))
        colors = [CIELCHuv_to_rgb(L, chroma, h) for h in np.linspace(0, 360, hue_samples)]

        for angle, color in zip(hue_angles, colors):
            ax.bar(angle, chroma, width=hue_angles[1] - hue_angles[0], color=color, edgecolor=color)

    ax.set_ylim(0, np.max(chroma_range))

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    ax.set_title('CIELCHuv Color Wheel at L* = ' + str(L))

    name = "lchuv_L_" + str(L) + ".png"
    plt.savefig(name)
    plt.show()

    # Create a color wheel for HSL
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    hue_samples = 360

    saturation_range = np.linspace(0, 1, num=6)

    width = 2 * np.pi / hue_samples

    for saturation in saturation_range:
        hue_angles_deg = np.linspace(0, 360, hue_samples)
        for h in hue_angles_deg:
            angle = np.radians(h)
            color = HSL_to_rgb(h, saturation, L/100)
            ax.bar(angle, saturation*100, width=width, color=color, edgecolor=color)

    ax.set_ylim(0, 100)

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)


    ax.set_title('HSL Color Wheel at L = ' + str(L))


    name = f"HSL_L_{L}.png"
    plt.savefig(name)
    plt.show()
