# Python3.7-Imaris-XTensions
XTensions built using Python 3.7 for Imaris software
1.	Measure intensity of Filament objects<br>
  a.	Dendrite mean intensity (for each channel)<br>
  b.	Filament mean intensity (for each channel)<br>
  c.	Spine intensity (not just the spine head, the whole spine)<br>
2.	Export Filament as a Spots object<br>
  a.	Place a spot at each point along the Filament, allowing for visualizing and measuring the localized intensity along segments<br>
    i.	It will fill gaps with spots between points that have spaces larger than the radius of dendrite at the point<br>
3.	Detect Boutons (varicosities) <br>
  a.	Finds swellings along each dendrite segment and places a spot at that point<br>
  b.	Diameter calculation is required for this to work<br>
  c.	NOTE: Filament diameter must be rendered properly for this to work properly <br>
4.	Find Spots Close to Filaments<br>
  a.	Detects the Spots within a defined distance threshold to each segment<br>
    i.	Quantifies number and density per segment<br>
    ii.	Quantifies number per Filament<br>
  b.	Calculates the Shortest Distance to Filament for each spot<br>
  c.	Measures colocalized Spot distances along dendrite to starting point<br>
    i.	Filament must have a Beginning Point<br>
5.	Neuronal Self Avoidance<br>
  a.	Detects when dendrite segment contacts another dendrite segment from same Filament<br>
  b.	Quantifies number of contacts per dendrite segment<br>
    i.	Option to remove contacts near starting point<br>
  c.	Measures the length of each contact<br>
    i.	Represented by Spot size<br>
6.	Neuron to Neuron contacts<br>
  a.	Detects when dendrite segment contacts a different segment from different Filament object<br>
  b.	Quantifies number of contacts per dendrite segment<br>
  c.	Measures the length each contact<br>
    i.	Represented by Spot size<br>
  d.	<b>NOTE:</b> current workflow is to have 2 separate Filament objects in the Surpass scene<br>
