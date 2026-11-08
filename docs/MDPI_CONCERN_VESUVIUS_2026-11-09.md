# SENT 9 Nov 2026, 08:04 AEST, from hassanrasheid@hotmail.com. Text below is exactly as sent.

To: remotesensing@mdpi.com
Cc: dme-remotesensing@mdpi.com
Subject: Concern regarding Remote Sensing 2022, 14(15), 3828 (Biondi, "Scanning Inside Volcanoes with SAR Echography Tomographic Doppler Imaging")

Dear Editorial Office,

I am writing to raise concerns about the article "Scanning Inside Volcanoes with Synthetic Aperture Radar Echography Tomographic Doppler Imaging" (F. Biondi, Remote Sensing 2022, 14(15), 3828, doi:10.3390/rs14153828), in the light of the retraction of Biondi and Malanga, Remote Sensing 2022, 14(20), 5231 (retraction notice doi:10.3390/rs18162679, 10 August 2026).

The two articles use the same core method: a single SAR single-look-complex image is split into Doppler sub-apertures, pixel tracking estimates a displacement for each sub-aperture, and a discrete Fourier transform across the sub-apertures is presented as a depth profile. The retraction of the Giza paper cited methodological and statistical issues, and I ask the Board to examine whether analogous issues affect the Vesuvius article, which remains published without any notice. Each point below can be checked against the article itself or against public data.

1. The depth scale is set by the analyst, not measured. Section 2.1 gives the resolution as δz = λR/(2A), with λ = v/f, a seismic velocity of about 972 m/s (given without a source, and about half the 2.0 km/s the article itself cites, in its reference [5], for a low-velocity magmatic layer) and "a frequency of investigation set by us equal to 200 Hz". With R = 650,000 m and A = 42,000 m this gives the stated resolution of about 36 m (the arithmetic gives 37.6 m). This is the standard SAR resolution relation with an acoustic wavelength put in place of the radar wavelength. With the radar wavelength (about 3.1 cm), the same numbers return about 0.24 m, the sub-metre scale of the image's own azimuth resolution. A is an along-track synthetic-aperture length from a single pass, not a baseline across the depth direction. Equation (10) builds the steering matrix from K_z = 4πB⊥/(λ r_i sin θ), the standard multi-pass tomography wavenumber, which requires a spread of perpendicular baselines B⊥ between separate acquisitions; a single pass provides none. The depth axis in metres therefore scales directly with the chosen v and f. Consistent with this, Figure 12 is said to give "the same results" at a lower vibrational frequency.

2. The seismograph comparison in Section 4.2 appears incompatible with the published station metadata. Table 2 lists stations IV.VCRE and IV.VBKN, channel HH. INGV's public station metadata (FDSN station service, network IV) give both stations' HH channels a sample rate of 100 samples per second, with Güralp CMG-40T sensors (60 s to 100 Hz), on station epochs open since 2008 (VCRE) and 2009 (VBKN), which cover the 2022 acquisition. A record sampled at 100 Hz contains no information above 50 Hz. Yet Figures 20(a,b) and 22(a,b) plot the "in-situ seismograph" spectrum from about −22 kHz to +22 kHz, and Figures 20(c) and 22(c) to about ±4 kHz and ±1.3 kHz, with structured energy far above 50 Hz. The station curves are also given in units of "pixel". The article does not say how the station data were obtained, resampled or converted. The stated investigation frequency of 200 Hz is likewise above both the stations' 50 Hz limit and the sensors' 100 Hz upper corner.

3. The acquisition date is inconsistent. Table 1 gives the acquisition date as 17 January 2022. Section 4.3 states that February 2022 "is the month in which the SAR data was acquired", and uses the February earthquakes as the events that coincide with the tomogram.

4. The other validation is visual. The DEM and magnetotelluric comparisons in Sections 4.1 and 4.3 are overlays judged by eye. No null test, uncertainty estimate or quantitative agreement measure is reported. Because the tomogram is geocoded in three dimensions (Section 2.3, block 11), its upper boundary can be placed by the geocoding itself, so agreement with topography does not by itself test the depth inference.

5. An independent reproduction did not find the claimed signal. My preprint (H. Foreman, "No Reproducible Evidence for Deep Subsurface Structures Beneath the Giza Plateau: A Controlled Reproduction of Single-Source SAR Doppler Micro-Motion Tomography", Zenodo, doi:10.5281/zenodo.21066657, latest version 14 August 2026; open code and data doi:10.5281/zenodo.21065675) rebuilt the published method from the article, the related Giza paper and the author's lapsed patent (WO2024008365A1), and applied it with null and positive controls to free X-band spotlight data, including an Umbra scene of Vesuvius (15 November 2023). At Vesuvius the output was a surface-pinned feature statistically indistinguishable from its null, while an in-data positive control (a reflector planted in the same scene) was recovered, showing the pipeline would have surfaced a genuine signal. I note the limitation plainly: this is a different sensor and date from the COSMO-SkyMed image used in the article, which, like the article's processing software, is not publicly available.

I would be grateful if the Editorial Board would examine these points, and ask the author for the raw station records and time windows used in Section 4.2, the processing parameters (number of sub-apertures, velocity, investigation frequency), and the code needed to reproduce the figures.

For transparency: I am an independent researcher with no financial interest in this matter. I am the author of the reproduction cited above. I have no other relationship with the author.

Yours sincerely,
Hassan Foreman
Independent researcher
hassanrasheid@hotmail.com
