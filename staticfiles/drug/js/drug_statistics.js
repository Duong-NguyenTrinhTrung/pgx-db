// Define 14 and 7 color scheme 
// const color14s = d3.range(257).map(d => d3.interpolateRainbow(d / 257));
// const color7s = d3.range(7).map(d => d3.interpolateRainbow(d / 7));
const color14s = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), 258);
const color7s = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), 4);
// Protein PieChart Function

function createPieChart_Drug_Category() {
    // Sample data
    const data = [
        { category: 'Cytochrome P-450 Substrates', value: 1081 },
        { category: 'Heterocyclic Compounds, Fused-Ring', value: 866 },
        { category: 'Cytochrome P-450 CYP3A Substrates', value: 820 },
        { category: 'Cytochrome P-450 CYP3A4 Substrates', value: 812 },
        { category: 'Cytochrome P-450 Enzyme Inhibitors', value: 665 },
        { category: 'Amino Acids, Peptides, and Proteins', value: 593 },
        { category: 'Enzyme Inhibitors', value: 529 },
        { category: 'Central Nervous System Agents', value: 505 },
        { category: 'Central Nervous System Depressants', value: 483 },
        { category: 'Neurotransmitter Agents', value: 473 },
        { category: 'Drugs that are Mainly Renally Excreted', value: 470 },
        { category: 'Sulfur Compounds', value: 421 },
        { category: 'Antineoplastic Agents', value: 381 },
        { category: 'P-glycoprotein substrates', value: 369 },
        { category: 'Peripheral Nervous System Agents', value: 368 },
        { category: 'Anti-Infective Agents', value: 364 },
        { category: 'Nervous System', value: 352 },
        { category: 'Cardiovascular Agents', value: 346 },
        { category: 'QTc Prolonging Agents', value: 346 },
        { category: 'Cytochrome P-450 CYP3A Inhibitors', value: 346 },
        { category: 'Amines', value: 343 },
        { category: 'Cytochrome P-450 CYP3A4 Inhibitors', value: 326 },
        { category: 'Proteins', value: 319 },
        { category: 'P-glycoprotein inhibitors', value: 316 },
        { category: 'Benzene Derivatives', value: 292 },
        { category: 'Antineoplastic and Immunomodulating Agents', value: 290 },
        { category: 'Carbohydrates', value: 280 },
        { category: 'Cytochrome P-450 Enzyme Inducers', value: 279 },
        { category: 'Cytochrome P-450 CYP2D6 Substrates', value: 278 },
        { category: 'Agents that produce hypertension', value: 277 },
        { category: 'Hormones }, Hormone Substitutes }, and Hormone Antagonists', value: 271 },
        { category: 'Compounds used in a research }, industrial }, or household setting', value: 270 },
        { category: 'Amides', value: 265 },
        { category: 'Alimentary Tract and Metabolism', value: 261 },
        { category: 'Immunosuppressive Agents', value: 255 },
        { category: 'Agents causing hyperkalemia', value: 244 },
        { category: 'Cytochrome P-450 CYP2C9 Substrates', value: 240 },
        { category: 'Fused-Ring Compounds', value: 225 },
        { category: 'Narrow Therapeutic Index Drugs', value: 224 },
        { category: 'Cytochrome P-450 CYP2D6 Inhibitors', value: 222 },
        { category: 'Hormones', value: 221 },
        { category: 'Steroids', value: 220 },
        { category: 'Antiinfectives for Systemic Use', value: 218 },
        { category: 'Peptides', value: 217 },
        { category: 'Lipids', value: 216 },
        { category: 'Antidepressive Agents', value: 215 },
        { category: 'Cytochrome P-450 CYP3A Inducers', value: 209 },
        { category: 'Cytochrome P-450 CYP1A2 Substrates', value: 207 },
        { category: 'Cytochrome P-450 CYP3A5 Substrates', value: 206 },
        { category: 'Blood Proteins', value: 198 },
        { category: 'Cytochrome P-450 CYP3A4 Inducers', value: 197 },
        { category: 'Acids, Acyclic', value: 197 },
        { category: 'Cytochrome P-450 CYP2C19 Substrates', value: 194 },
        { category: 'Serotonergic Drugs Shown to Increase Risk of Serotonin Syndrome', value: 193 },
        { category: 'Anti-Bacterial Agents', value: 190 },
        { category: 'Agents producing tachycardia', value: 188 },
        { category: 'Sensory System Agents', value: 184 },
        { category: 'Dermatologicals', value: 183 },
        { category: 'Cytochrome P-450 CYP3A4 Inhibitors (strength unknown)', value: 180 },
        { category: 'Potential QTc-Prolonging Agents', value: 180 },
        { category: 'Serotonin Agents', value: 179 },
        { category: 'Analgesics', value: 173 },
        { category: 'Genito Urinary System and Sex Hormones', value: 172 },
        { category: 'Biological Factors', value: 171 },
        { category: 'Cytochrome P-450 CYP2C9 Inhibitors', value: 170 },
        { category: 'Hypotensive Agents', value: 168 },
        { category: 'Glycosides', value: 168 },
        { category: 'Anti-Inflammatory Agents', value: 167 },
        { category: 'Alcohols', value: 166 },
        { category: 'Amino Acids', value: 166 },
        { category: 'Autonomic Agents', value: 166 },
        { category: 'Acids, Carbocyclic', value: 165 },
        { category: 'Serum Globulins', value: 164 },
        { category: 'Membrane Transport Modulators', value: 164 },
        { category: 'Cytochrome P-450 CYP1A2 Inhibitors', value: 162 },
        { category: 'Fatty Acids', value: 162 },
        { category: 'Alkaloids', value: 158 },
        { category: 'Cytochrome P-450 CYP2C8 Substrates', value: 158 },
        { category: 'Immunoglobulins', value: 157 },
        { category: 'Globulins', value: 153 },
        { category: 'Immunoproteins', value: 151 },
        { category: 'Cytochrome P-450 CYP3A4 Inducers (strength unknown)', value: 150 },
        { category: 'Psychotropic Drugs', value: 150 },
        { category: 'Antihypertensive Agents', value: 150 },
        { category: 'Adrenal Cortex Hormones', value: 147 },
        { category: 'Antibodies', value: 145 },
        { category: 'Cytochrome P-450 CYP2C19 Inhibitors', value: 145 },
        { category: 'Cytochrome P-450 CYP2C8 Inhibitors', value: 144 },
        { category: 'Ophthalmologicals', value: 143 },
        { category: 'Vasodilating Agents', value: 142 },
        { category: 'OATP1B1/SLCO1B1 Inhibitors', value: 141 },
        { category: 'Photosensitizing Agents', value: 140 },
        { category: 'Sensory Organs', value: 139 },
        { category: 'Bradycardia-Causing Agents', value: 138 },
        { category: 'Adrenergic Agents', value: 138 },
        { category: 'Anticholinergic Agents', value: 133 },
        { category: 'Nephrotoxic agents', value: 131 },
        { category: 'Toxic Actions', value: 130 },
        { category: 'Nucleic Acids, Nucleotides, and Nucleosides', value: 130 },
        { category: 'Antiarrhythmic agents', value: 130 },
        { category: 'Drugs causing inadvertant photosensitivity', value: 128 },
        { category: 'Antibacterials for Systemic Use', value: 126 },
        { category: 'Pyridines', value: 126 },
        { category: 'BCRP/ABCG2 Substrates', value: 126 },
        { category: 'Cytochrome P-450 CYP2C9 Inhibitors (strength unknown)', value: 123 },
        { category: 'BCRP/ABCG2 Inhibitors', value: 122 },
        { category: 'Blood and Blood Forming Organs', value: 120 },
        { category: 'OAT1/SLC22A6 inhibitors', value: 120 },
        { category: 'Sulfones', value: 120 },
        { category: 'Antibodies, Monoclonal', value: 118 },
        { category: 'Cytochrome P-450 CYP1A2 Inhibitors (strength unknown)', value: 117 },
        { category: 'Hematologic Agents', value: 116 },
        { category: 'Purines', value: 116 },
        { category: 'Myelosuppressive Agents', value: 115 },
        { category: 'Gastrointestinal Agents', value: 115 },
        { category: 'Hyperglycemia-Associated Agents', value: 114 },
        { category: 'Musculo-Skeletal System', value: 112 },
        { category: 'Noxae', value: 109 },
        { category: 'Cytochrome P-450 CYP2D6 Inhibitors (strength unknown)', value: 109 },
        { category: 'Psycholeptics', value: 109 },
        { category: 'Adrenergic Antagonists', value: 109 },
        { category: 'Cytochrome P-450 CYP3A4 Substrates with a Narrow Therapeutic Index', value: 108 },
        { category: 'Cytochrome P-450 CYP3A7 Substrates', value: 108 },
        { category: 'Protective Agents', value: 105 },
        { category: 'Antirheumatic Agents', value: 104 },
        { category: 'Serotonin Receptor Antagonists', value: 104 },
        { category: 'Neurotoxic agents', value: 103 },
        { category: 'Pyrimidines', value: 103 },
        { category: 'Moderate Risk QTc-Prolonging Agents', value: 100 },
        { category: 'Histamine Antagonists', value: 100 },
        { category: 'Phenols', value: 99 },
        { category: 'Analgesics, Non-Narcotic', value: 98 },
        { category: 'Benzoates', value: 97 },
        { category: 'Fatty Acids, Volatile', value: 97 },
        { category: 'Cytochrome P-450 CYP2B6 Substrates', value: 96 },
        { category: 'OAT3/SLC22A8 Inhibitors', value: 95 },
        { category: 'Muscarinic Antagonists', value: 94 },
        { category: 'Tranquilizing Agents', value: 93 },
        { category: 'Agents Causing Muscle Toxicity', value: 92 },
        { category: 'Histamine H1 Antagonists', value: 91 },
        { category: 'Agents that reduce seizure threshold', value: 90 },
        { category: 'Antiviral Agents', value: 89 },
        { category: 'UGT1A1 Substrates', value: 88 },
        { category: 'Dopamine Agents', value: 86 },
        { category: 'Protein Kinase Inhibitors', value: 86 },
        { category: 'Amino Alcohols', value: 85 },
        { category: 'Pregnanes', value: 85 },
        { category: 'Protease Inhibitors', value: 84 },
        { category: 'Respiratory System Agents', value: 83 },
        { category: 'Cytochrome P-450 CYP2C19 inhibitors (strength unknown)', value: 83 },
        { category: 'Antibodies, Monoclonal, Humanized', value: 82 },
        { category: 'OCT2 Inhibitors', value: 79 },
        { category: 'Immunotherapy', value: 78 },
        { category: 'Enzymes and Coenzymes', value: 78 },
        { category: 'Immunologic Factors', value: 78 },
        { category: 'P-glycoprotein substrates with a Narrow Therapeutic Index', value: 78 },
        { category: 'OAT3/SLC22A8 Substrates', value: 78 },
        { category: 'Blood Glucose Lowering Agents', value: 77 },
        { category: 'BSEP/ABCB11 Substrates', value: 77 },
        { category: 'Acids', value: 77 },
        { category: 'Acids, Noncarboxylic', value: 77 },
        { category: 'Hydroxy Acids', value: 77 },
        { category: 'Adrenergic Agonists', value: 77 },
        { category: 'Nucleotides', value: 76 },
        { category: 'Cholinergic Agents', value: 75 },
        { category: 'Cytochrome P-450 CYP2E1 Substrates', value: 75 },
        { category: 'Terpenes', value: 75 },
        { category: 'Anti-Inflammatory Agents, Non-Steroidal', value: 75 },
        { category: 'Cytochrome P-450 CYP2C8 Inhibitors (strength unknown)', value: 75 },
        { category: 'Serotonin 5-HT2 Receptor Antagonists', value: 75 },
        { category: 'Serotonin Modulators', value: 74 },
        { category: 'Corticosteroids', value: 74 },
        { category: 'Indoles', value: 74 },
        { category: 'Calcium Channel Blockers', value: 74 },
        { category: 'OATP1B3 inhibitors', value: 72 },
        { category: 'Quinolines', value: 72 },
        { category: 'Psychoanaleptics', value: 71 },
        { category: 'Anticonvulsants', value: 71 },
        { category: 'Peptide Hormones', value: 70 },
        { category: 'Cytochrome P-450 CYP3A4 Substrates (strength unknown)', value: 70 },
        { category: 'Anticoagulants', value: 69 },
        { category: 'Kinase Inhibitor', value: 69 },
        { category: 'Adrenergic alpha-Antagonists', value: 68 },
        { category: 'Dopamine Antagonists', value: 68 },
        { category: 'OATP1B1/SLCO1B1 Substrates', value: 67 },
        { category: 'Antivirals for Systemic Use', value: 67 },
        { category: 'Direct Acting Antivirals', value: 67 },
        { category: 'Antipsychotic Agents', value: 67 },
        { category: 'Calcium-Regulating Hormones and Agents', value: 66 },
        { category: 'Cycloparaffins', value: 66 },
        { category: 'Cytochrome P-450 CYP2B6 Inhibitors', value: 66 },
        { category: 'Antiparasitic Agents', value: 66 },
        { category: 'Cytochrome P-450 CYP3A4 Inhibitors (weak)', value: 66 },
        { category: 'Cancer immunotherapy', value: 65 },
        { category: 'Cytochrome P-450 CYP2D6 Inhibitors (weak)', value: 65 },
        { category: 'Diet, Food, and Nutrition', value: 65 },
        { category: 'Food', value: 65 },
        { category: 'Pyrans', value: 64 },
        { category: 'Antihypertensive Agents Indicated for Hypertension', value: 64 },
        { category: 'P-glycoprotein inducers', value: 64 },
        { category: 'Histamine Agents', value: 64 },
        { category: 'Cytochrome P-450 CYP2E1 Inhibitors', value: 63 },
        { category: 'Growth Substances', value: 63 },
        { category: 'Cytochrome P-450 CYP2B6 Inducers', value: 63 },
        { category: 'Lactones', value: 63 },
        { category: 'Cardiac Therapy', value: 63 },
        { category: 'Dopamine D2 Receptor Antagonists', value: 63 },
        { category: 'Systemic Hormonal Preparations, Excl. Sex Hormones and Insulins', value: 62 },
        { category: 'Gynecological Antiinfectives and Antiseptics', value: 62 },
        { category: 'Drugs for Obstructive Airway Diseases', value: 62 },
        { category: 'Tyrosine Kinase Inhibitors', value: 62 },
        { category: 'Physiological Phenomena', value: 61 },
        { category: 'Cytochrome P-450 CYP3A5 Inhibitors', value: 61 },
        { category: 'Lactams', value: 61 },
        { category: 'Serotonin 5-HT2A Receptor Antagonists', value: 61 },
        { category: 'Reproductive Control Agents', value: 60 },
        { category: 'Hypnotics and Sedatives', value: 60 },
        { category: 'UGT2B7 substrates', value: 60 },
        { category: 'Piperidines', value: 60 },
        { category: 'Hypoglycemia-Associated Agents', value: 59 },
        { category: 'Vitamins', value: 59 },
        { category: 'OCT1 inhibitors', value: 59 },
        { category: 'Hormone Antagonists', value: 58 },
        { category: 'Nucleosides', value: 58 },
        { category: 'UGT1A9 Substrates', value: 58 },
        { category: 'Sex Hormones and Modulators of the Genital System', value: 57 },
        { category: 'Anti-Asthmatic Agents', value: 57 },
        { category: 'Adrenergic alpha-1 Receptor Antagonists', value: 57 },
        { category: 'Anions', value: 55 },
        { category: 'Electrolytes', value: 55 },
        { category: 'Ions', value: 55 },
        { category: 'Supplements', value: 55 },
        { category: 'Nitrogen Compounds', value: 55 },
        { category: 'Cytochrome P-450 CYP3A5 Inducers', value: 55 },
        { category: 'Anesthetics', value: 55 },
        { category: 'Aniline Compounds', value: 55 },
        { category: 'Gonadal Hormones', value: 55 },
        { category: 'Gonadal Steroid Hormones', value: 55 },
        { category: 'Sulfonamides', value: 54 },
        { category: 'Highest Risk QTc-Prolonging Agents', value: 54 },
        { category: 'Antiinflammatory and Antirheumatic Products', value: 54 },
        { category: 'Drugs Used in Diabetes', value: 53 },
        { category: 'Cholinesterase Inhibitors', value: 53 },
        { category: 'Pregnadienes', value: 53 },
        { category: 'Cytochrome P-450 CYP1A2 Inducers', value: 52 },
        { category: 'Dietary Supplements', value: 52 },
        { category: 'OATP1B3 substrates', value: 52 },
        { category: 'Oligopeptides', value: 51 },
        { category: 'Cytochrome P-450 CYP2D6 Inhibitors (moderate)', value: 51 },
        { category: 'Neurotransmitter Uptake Inhibitors', value: 51 },
        { category: 'MATE inhibitors', value: 51 },
        { category: 'Polyketides', value: 51 },
        { category: 'Amino Acids, Cyclic', value: 50 },
        { category: 'Imidazoles', value: 50 },
        { category: 'Non COX-2 selective NSAIDS', value: 50 },
        { category: 'Benzopyrans', value: 50 },
        { category: 'Antiprotozoals', value: 50 },
        { category: 'Other', value: 21076 },
       ];
    // alert("length of colors = "+data.length);
    const container = document.getElementById("chart-container1");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drug-category")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    // Creates a pie generator function using D3, which will convert the data into angles for the pie chart.
    const pie = d3.pie()
        .value(d => d.value);

    // Defines an arc generator to draw the slices of the pie chart, with specified inner and outer radius
    const arc = d3.arc()
        .innerRadius(radius - 40)
        .outerRadius(radius - 10);

    // color is a function
    const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), 257);
    // const color = d3.scaleOrdinal(color14s);
    const color = d3.scaleOrdinal(colors);

    //Appends a g (group) element to the SVG and centers it, which will contain the pie chart.
    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    // Selects all elements with class arc, binds the pie data to them, enters the data join, appends g elements 
    // for each data point, and assigns the class arc.
    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container1")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0); //opacity of 0 (hidden)

    //Appends path elements to each g element in arcs, representing slices of the pie chart.
    arcs.append("path")
        //Sets the 'd' attribute of each path using the arc function defined earlier. This attribute defines the shape of the pie slices.
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            // Slightly increase the outerRadius of the specific slice on mouseover
            const newArc = d3.arc()
                .innerRadius(radius -35)
                .outerRadius(radius - 5); // Adjust the value as needed

            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", newArc);

            const tooltipText = `${d.data.category}: ${d.data.value}`;
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
            tooltip.html(tooltipText)
                .style("left", (container.offsetLeft+ size/2 -28) + "px")
                .style("top", (container.offsetTop + size/2) + "px");
        })
        .on("mouseout", function () {
            // Restore the original arc when mouseout
            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", arc);

            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
}


function createPieChart_MOA() {
    // Main categories data
    const data = [
        { category: "Target", value: 14030 },
        { category: "Enzyme", value: 5278 },
        { category: "Transporter", value: 3205 },
        { category: "Carrier", value: 822 },
    ];

    // Subcategories data for "Enzyme"
    const enzyme_subcategories = [
        { category: "substrate", value: 2871 },
        { category: "inhibitor", value: 1133 },
        { category: "substrate|inhibitor", value: 472 },
        { category: "inducer", value: 424 },
        { category: "substrate|inducer", value: 156 },
        { category: "substrate|inhibitor|inducer", value: 57 },
        { category: "inhibitor|inducer", value: 50 },
        { category: "ligand", value: 27 },
        { category: "cofactor", value: 20 },
        { category: "other", value: 49  }
    ];
    // Subcategories data for "Target"
    const target_subcategories = [
        { category: "inhibitor", value: 2239 },
        { category: "antagonist", value: 1522 },
        { category: "agonist", value: 1142 },
        { category: "binder", value: 321 },
        { category: "ligand", value: 275 },
        { category: "cofactor", value: 190 },
        { category: "activator", value: 152 },
        { category: "potentiator", value: 140 },
        { category: "inducer", value: 98 },
        { category: "substrate", value: 69 },
        { category: "partial agonist", value: 68 },
        { category: "other/unknown", value: 660 }
    ];
    // Subcategories data for "Transporter"
    const transporter_subcategories = [
        { category: "inhibitor", value: 1214 },
        { category: "substrate", value: 1172 },
        { category: "substrate|inhibitor", value: 380 },
        { category: "inducer", value: 66 },
        { category: "substrate|inhibitor|inducer", value: 31 },
        { category: "inhibitor|inducer", value: 19 },
        { category: "substrate|inducer", value: 19 },
        { category: "transporter", value: 6 },
        { category: "other", value: 23 },
    ];
    // Subcategories data for "Carrier"
    const carrier_subcategories = [
        { category: "binder", value: 340 },
        { category: "substrate", value: 130 },
        { category: "other/unknown", value: 20 },
        { category: "carrier", value: 14 },
        { category: "inducer", value: 12 },
        { category: "inhibitor", value: 8 },
        { category: "ligand", value: 6 },
        { category: "antagonist", value: 3 },
        { category: "agonist", value: 2 },
        { category: "substrate|inhibitor", value: 1 }
    ];

    const container = document.getElementById("chart-container2");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-MOA-category")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${size} ${size}`);

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius -40)
        .outerRadius(radius - 10);

    const nestedArc = d3.arc()
        .innerRadius(radius - 10)
        .outerRadius(radius);

    // const color = d3.scaleOrdinal(d3.schemeCategory10);
    const color = d3.scaleOrdinal(color7s);
    const subcategoryColor = d3.scaleOrdinal([
        "#1e81b0", "#e28743", "#76b5c5", "#21130d", "#873e23", "#063970", "#eab676", "#154c79"
    ]);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`);

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container2")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0)
        .style("text-align", "left");

    function show_sub_category(x, y, d, subcategories, tooltipHtml){
        const nestedPie = d3.pie()
                    .value(d => d.value)
                    .startAngle(d.startAngle)
                    .endAngle(d.endAngle)(subcategories);

                g.selectAll(".nested-arc")
                    .data(nestedPie)
                    .enter()
                    .append("path")
                    .attr("class", "nested-arc")
                    .attr("d", nestedArc)
                    .style("fill", (d, i) => subcategoryColor(d.data.category));

                subcategories.forEach(sub => {
                    tooltipHtml += `<span style='color: ${subcategoryColor(sub.category)}; font-size:8px;'>●</span> ${sub.category} (${sub.value})<br>`;
                });

                tooltip.html(tooltipHtml)
                    .style("opacity", 1)
                    // .style("left", `${x + 10}px`)
                    // .style("top", `${y + 10}px`);
                    .style("left", `${x + 10}px`)
                    .style("top", `${y-50}px`);
    }

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            const [x, y] = d3.pointer(event, svg.node());

            if (d.data.category === "Target") {
                tooltipHtml = "Target - 14030 :<br>";
                show_sub_category(x-50, y+50, d, target_subcategories, tooltipHtml)
            } 
            else 
            {
                if (d.data.category === "Enzyme") {
                    tooltipHtml = "Enzyme - 5278 :<br>";
                    show_sub_category(x+100, y, d, enzyme_subcategories, tooltipHtml)
                }
                else
                {
                    if (d.data.category === "Transporter") {
                        tooltipHtml = "Transporter - 3205 :<br>";
                        show_sub_category(x+150, y+50, d, transporter_subcategories, tooltipHtml)
                    }
                    else{
                        tooltipHtml = "Carrier - 822 :<br>";
                        show_sub_category(x+160, y+50, d, carrier_subcategories, tooltipHtml)
                        }
                }
            }
        })
        .on("mouseout", function () {
            g.selectAll(".nested-arc").remove();
            tooltip.style("opacity", 0);
        });
}



// Pie 

function createPieChart_Drug_Superclass() {
    // Main categories data
    const data = [
        { category: "Organoheterocyclic compounds", value: 1692 },
        { category: "Benzenoids", value: 1217 },
        { category: "Organic acids and derivatives", value: 839 },
        { category: "None", value: 674 },
        { category: "Lipids and lipid-like molecules", value: 450 },
        { category: "Organic oxygen compounds", value: 307 },
        { category: "Phenylpropanoids and polyketides", value: 215 },
        { category: "Nucleosides, nucleotides, and analogues", value: 172 },
        { category: "Organic nitrogen compounds", value: 119 },
        { category: "Alkaloids and derivatives", value: 75 },
        { category: "Mixed metal/non-metal compounds", value: 33 },
        { category: "Organosulfur compounds", value: 26 },
        { category: "Organic Polymers", value: 20 },
        { category: "Homogeneous non-metal compounds", value: 11 },
        { category: "Homogeneous metal compounds", value: 9 },
        { category: "Organohalogen compounds", value: 8 },
        { category: "Lignans, neolignans and related compounds", value: 8 },
        { category: "Organophosphorus compounds", value: 8 },
        { category: "Organometallic compounds", value: 3 },
        { category: "Organic salts", value: 1 },
        { category: "Hydrocarbon derivatives", value: 1 },
       ];
    // alert("length of colors = "+data.length);
    const container = document.getElementById("chart-container3");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drug-superclass")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    // Creates a pie generator function using D3, which will convert the data into angles for the pie chart.
    const pie = d3.pie()
        .value(d => d.value);

    // Defines an arc generator to draw the slices of the pie chart, with specified inner and outer radius
    const arc = d3.arc()
        .innerRadius(radius - 40)
        .outerRadius(radius - 10);

    // color is a function
    const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), 21);
    // const color = d3.scaleOrdinal(color14s);
    const color = d3.scaleOrdinal(colors);

    //Appends a g (group) element to the SVG and centers it, which will contain the pie chart.
    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    // Selects all elements with class arc, binds the pie data to them, enters the data join, appends g elements 
    // for each data point, and assigns the class arc.
    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container3")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0); //opacity of 0 (hidden)

    //Appends path elements to each g element in arcs, representing slices of the pie chart.
    arcs.append("path")
        //Sets the 'd' attribute of each path using the arc function defined earlier. This attribute defines the shape of the pie slices.
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            // Slightly increase the outerRadius of the specific slice on mouseover
            const newArc = d3.arc()
                .innerRadius(radius -35)
                .outerRadius(radius - 5); // Adjust the value as needed

            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", newArc);

            const tooltipText = `${d.data.category}: ${d.data.value}`;
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
            tooltip.html(tooltipText)
                .style("left", (container.offsetLeft+ size/2 -28) + "px")
                .style("top", (container.offsetTop + size/2) + "px");
        })
        .on("mouseout", function () {
            // Restore the original arc when mouseout
            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", arc);

            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
}


// Pie 

function createPieChart4() {
    // Main categories data
    const data = [
        { category: "Small molecule", value: 5827 },
        { category: "Biotech", value: 432 },
       ];
    // alert("length of colors = "+data.length);
    const container = document.getElementById("chart-container4");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drug-type")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    // Creates a pie generator function using D3, which will convert the data into angles for the pie chart.
    const pie = d3.pie()
        .value(d => d.value);

    // Defines an arc generator to draw the slices of the pie chart, with specified inner and outer radius
    const arc = d3.arc()
        .innerRadius(radius - 40)
        .outerRadius(radius - 10);

    // color is a function
    const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), 2);
    // const color = d3.scaleOrdinal(color14s);
    const color = d3.scaleOrdinal(colors);

    //Appends a g (group) element to the SVG and centers it, which will contain the pie chart.
    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    // Selects all elements with class arc, binds the pie data to them, enters the data join, appends g elements 
    // for each data point, and assigns the class arc.
    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container4")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0); //opacity of 0 (hidden)

    //Appends path elements to each g element in arcs, representing slices of the pie chart.
    arcs.append("path")
        //Sets the 'd' attribute of each path using the arc function defined earlier. This attribute defines the shape of the pie slices.
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            // Slightly increase the outerRadius of the specific slice on mouseover
            const newArc = d3.arc()
                .innerRadius(radius -35)
                .outerRadius(radius - 5); // Adjust the value as needed

            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", newArc);

            const tooltipText = `${d.data.category}: ${d.data.value}`;
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
            tooltip.html(tooltipText)
                .style("left", (container.offsetLeft+ size/2 -28) + "px")
                .style("top", (container.offsetTop + size/2) + "px");
        })
        .on("mouseout", function () {
            // Restore the original arc when mouseout
            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", arc);

            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
}


createPieChart_Drug_Category();
// createPieChart_MOA();
createPieChart_Drug_Superclass()
createPieChart4()