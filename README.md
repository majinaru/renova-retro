## Renova Retro

Renova Retro is a website that employs an innovative algorithm to derive a resolution-independent vector representation from pixel art images. This algorithm allows for magnification of the results by any scale without compromising image quality. It effectively resolves pixel-scale features in the input and transforms them into regions with smoothly varying shading, distinctly separated by piecewise-smooth contour curves.

In the original image, pixels are depicted on a square pixel lattice, where diagonal neighbors are connected only through a single point. This characteristic causes thin features to visually disconnect under conventional magnification methods and introduces ambiguities in the connectedness and separation of diagonal neighbors. The crux of our algorithm lies in resolving these ambiguities, facilitating the restructuring of pixel cells so that neighboring pixels belonging to the same feature are connected through edges, thus maintaining feature connectivity during magnification. We mitigate pixel aliasing artifacts and enhance smoothness by employing spline curves to fit contours in the image and optimizing their control points.

## How to Use

To run the website local, you need to initiate the Flask server located in the "Backend" folder using the following command:

```bash
python3 server.py
```

It's crucial to ensure that you have installed the Angular CLI and all the necessary libraries for executing server.py. Double-check that all required libraries are installed in your environment. Furthermore, you should initiate the Angular server by running the following command within the "renova-retro" folder:

```bash
ng serve
```

## Reference

This website is a direct application of the algorithm described by Johannes Kopf and Dani Lischinski of The Hebrew University. Their paper is titled Depixelizing Pixel Art
