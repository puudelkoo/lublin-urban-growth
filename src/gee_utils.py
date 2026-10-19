"""
Reusable Google Earth Engine helper functions for the Lublin land-cover
change analysis.

The module contains functions for:
- preprocessing Landsat 5 and Landsat 8 Collection 2 Level-2 imagery,
- calculating NDVI and NDBI spectral indices,
- creating seasonal median composites,
- splitting training polygons into training and testing subsets,
- extracting predictor values from training polygons.

The functions are shared between multiple notebooks to avoid duplicated
processing logic and to ensure methodological consistency across the project.
"""

import ee


def preprocess_landsat5(image):
    """
    Preprocess a Landsat 5 TM Collection 2 Level-2 image.

    The function:
    - removes fill pixels, dilated clouds, clouds, cloud shadows and snow
      using the QA_PIXEL band,
    - removes radiometrically saturated pixels using QA_RADSAT,
    - applies the Collection 2 Level-2 surface-reflectance scaling,
    - selects the optical bands required for the analysis,
    - renames the bands to a common cross-sensor naming scheme.

    The resulting bands are:
    blue, green, red, nir, swir1 and swir2.

    Parameters
    ----------
    image : ee.Image
        Landsat 5 Collection 2 Level-2 image.

    Returns
    -------
    ee.Image
        Preprocessed and masked image with harmonized optical band names.
    """
    qa = image.select("QA_PIXEL")
    radsat = image.select("QA_RADSAT")

    mask = (
        qa.bitwiseAnd(1 << 0)
        .eq(0)
        .And(qa.bitwiseAnd(1 << 1).eq(0))
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
        .And(qa.bitwiseAnd(1 << 5).eq(0))
        .And(radsat.eq(0))
    )

    optical = (
        image.select(
            ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"],
            ["blue", "green", "red", "nir", "swir1", "swir2"],
        )
        .multiply(0.0000275)
        .add(-0.2)
    )

    return optical.updateMask(mask).copyProperties(image, ["system:time_start"])


def preprocess_landsat8(image):
    """
    Preprocess a Landsat 8 OLI Collection 2 Level-2 image.

    The function:
    - removes fill pixels, dilated clouds, cirrus, clouds, cloud shadows
      and snow using the QA_PIXEL band,
    - removes radiometrically saturated pixels using QA_RADSAT,
    - applies the Collection 2 Level-2 surface-reflectance scaling,
    - selects the optical bands required for the analysis,
    - renames the bands to the same naming scheme used for Landsat 5.

    The resulting bands are:
    blue, green, red, nir, swir1 and swir2.

    Parameters
    ----------
    image : ee.Image
        Landsat 8 Collection 2 Level-2 image.

    Returns
    -------
    ee.Image
        Preprocessed and masked image with harmonized optical band names.
    """
    qa = image.select("QA_PIXEL")
    radsat = image.select("QA_RADSAT")

    mask = (
        qa.bitwiseAnd(1 << 0)
        .eq(0)
        .And(qa.bitwiseAnd(1 << 1).eq(0))
        .And(qa.bitwiseAnd(1 << 2).eq(0))
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
        .And(qa.bitwiseAnd(1 << 5).eq(0))
        .And(radsat.eq(0))
    )

    optical = (
        image.select(
            ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"],
            ["blue", "green", "red", "nir", "swir1", "swir2"],
        )
        .multiply(0.0000275)
        .add(-0.2)
    )

    return optical.updateMask(mask).copyProperties(image, ["system:time_start"])


def add_indices(image):
    """
    Add NDVI and NDBI spectral indices to an image.

    NDVI is calculated as:
    (NIR - RED) / (NIR + RED)

    NDBI is calculated as:
    (SWIR1 - NIR) / (SWIR1 + NIR)

    Earth Engine expressions are used instead of normalizedDifference()
    so that negative reflectance values produced by Landsat Collection 2
    scaling are not automatically masked.

    Parameters
    ----------
    image : ee.Image
        Preprocessed image containing red, nir and swir1 bands.

    Returns
    -------
    ee.Image
        Input image with additional NDVI and NDBI bands.
    """
    ndvi = image.expression(
        "(NIR - RED) / (NIR + RED)",
        {"NIR": image.select("nir"), "RED": image.select("red")},
    ).rename("NDVI")

    ndbi = image.expression(
        "(SWIR1 - NIR) / (SWIR1 + NIR)",
        {"SWIR1": image.select("swir1"), "NIR": image.select("nir")},
    ).rename("NDBI")

    return image.addBands([ndvi, ndbi])


def create_composite(collection_id, start_date, end_date, aoi, preprocess_func):
    """
    Create a seasonal median Landsat composite.

    The selected image collection is filtered spatially and temporally,
    preprocessed using the supplied sensor-specific function and reduced
    to a median composite. The result is clipped to the Area of Interest.

    Parameters
    ----------
    collection_id : str
        Earth Engine Landsat ImageCollection identifier.
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        Exclusive end date in YYYY-MM-DD format.
    aoi : ee.Geometry
        Area of Interest used for filtering and clipping.
    preprocess_func : callable
        Sensor-specific preprocessing function applied to every image.

    Returns
    -------
    ee.Image
        Median seasonal composite clipped to the Area of Interest.
    """
    collection = (
        ee.ImageCollection(collection_id)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(preprocess_func)
    )

    return collection.median().clip(aoi)


def split_class(fc, class_id, n_test, seed):
    """
    Split polygons from one land-cover class into training and testing subsets.

    A deterministic random column is generated using the supplied seed.
    A fixed number of polygons is assigned to the testing subset and the
    remaining polygons are assigned to the training subset.

    Parameters
    ----------
    fc : ee.FeatureCollection
        FeatureCollection containing training polygons.
    class_id : int
        Numeric land-cover class identifier.
    n_test : int
        Number of polygons assigned to the testing subset.
    seed : int
        Random seed used to make the split reproducible.

    Returns
    -------
    tuple
        Training and testing ee.FeatureCollections.
    """
    class_fc = (
        fc.filter(ee.Filter.eq("class", class_id))
        .randomColumn("random", seed)
        .sort("random")
    )

    total = class_fc.size()

    test_fc = class_fc.limit(n_test)

    train_fc = class_fc.sort("random", False).limit(total.subtract(n_test))

    return train_fc, test_fc


def sample_year(image, polygons, predictor_bands):
    """
    Extract predictor values from an image using training polygons.

    Pixel values from the selected predictor bands are sampled within the
    supplied polygons at the native 30 m Landsat analysis scale. Class
    attributes are preserved in the resulting sample.

    Parameters
    ----------
    image : ee.Image
        Image containing the predictor bands.
    polygons : ee.FeatureCollection
        Training or testing polygons.
    predictor_bands : list
        Names of the predictor bands to sample.

    Returns
    -------
    ee.FeatureCollection
        Sampled pixels containing predictor values and class attributes.
    """
    return image.select(predictor_bands).sampleRegions(
        collection=polygons,
        properties=["class", "class_name"],
        scale=30,
        geometries=True,
    )
