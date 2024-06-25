// Define 14 and 7 color scheme 
const color14s = d3.range(14).map(d => d3.interpolateRainbow(d / 14));
const color7s = d3.range(7).map(d => d3.interpolateRainbow(d / 7));
// Protein PieChart Function
function createPieChart_Proteins() {
    // Sample data
    const data = [
        { category: "Adhesion ", value: 14 },
        { category: "Enzyme", value: 854 },
        { category: "Epigenetic regulator", value: 37 },
        { category: "GPCR", value: 163 },
        { category: "Ion channel", value: 160 },
        { category: "Kinase", value: 348 },
        { category: "Membrane receptor", value: 67 },
        { category: "Nuclear receptor", value: 59 },
        { category: "Secreted protein ", value: 85 },
        { category: "Structural protein ", value: 25 },
        { category: "Surface antigen ", value: 20 },
        { category: "Transcription factor ", value: 7 },
        { category: "Transporter ", value: 172 },
        { category: "Unknown ", value: 967 }
    ];

    const container = document.getElementById("chart-container1");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-proteins")
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
    const color = d3.scaleOrdinal(color14s);

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


// Drug PieChart Function
function createPieChart_Drugs() {
    const data = [
        { category: "Nutraceutical", value: 30 },
        { category: "Preclinical", value: 2975 },
        { category: "Investigational", value: 906 },
        { category: "Approved", value: 2277 },
        { category: "Vet-approved", value: 36 },
        { category: "Illicit", value: 35 }
    ];

    const container = document.getElementById("chart-container2");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drugs")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 40)
        .outerRadius(radius - 10);

    // const color = d3.scaleOrdinal(d3.schemeAccent);
    const color = d3.scaleOrdinal(color7s);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container2")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0);

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            // Slightly increase the outerRadius of the specific slice on mouseover
            const newArc = d3.arc()
                .innerRadius(radius - 35)
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


// ATC code level 1 PieChart Function
function createPieChart_ATClevel1() {
    const data = [
        { category: "Alimentary tract and metabolism", value: 422 },
        { category: "Blood and blood forming organs", value: 142 },
        { category: "Cardiovascular system", value: 533 },
        { category: "Dermatologicals", value: 220 },
        { category: "Genito urinary system and sex hormones", value: 327 },
        { category: "Systemic hormonal prep, excl sex hormones", value: 65 },
        { category: "General antiinfectives for systemic use", value: 380 },
        { category: "Antineoplastic and immunomodulating agents", value: 306 },
        { category: "Musculo-skeletal system", value: 167 },
        { category: "Nervous system", value: 445 },
        { category: "Antiparasitic products, insecticides and repellants", value: 65 },
        { category: "Respiratory system", value: 286 },
        { category: "Sensory organs", value: 226 },
        { category: "Various", value: 92 }
    ];

    const container = document.getElementById("chart-container3");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-ATC")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius -40)
        .outerRadius(radius - 10);

    const color = d3.scaleOrdinal(color14s);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container3")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0);

    arcs.append("path")
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

function createPieChart_Mutations() {
    // Main categories data
    const data = [
        { category: "Target", value: 14030 },
        { category: "Enzyme", value: 5278 },
        { category: "Transporter", value: 3205 },
        { category: "Carrier", value: 822 },
    ];

    // Subcategories data for "Target"
    const subcategories = [
        { category: "Enzyme", value: 3661 },
        { category: "Unknown", value: 3602 },
        { category: "GPCR", value: 2450 },
        { category: "Kinase", value: 1583 },
        { category: "Ion channel", value: 937 },
        { category: "Nuclear receptor", value: 867 },
        { category: "Transporter", value: 429 },
        { category: "Epigenetic regulator", value: 115 }
    ];

    const container = document.getElementById("chart-container4");
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-mutations")
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
    const color = d3.scaleOrdinal(color14s);
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

    const tooltip = d3.select("#chart-container4")
        .append("div")
        .attr("class", "tooltip1")
        .style("opacity", 0)
        .style("text-align", "left");

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            const [x, y] = d3.pointer(event, svg.node());

            if (d.data.category === "Target") {
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

                let tooltipHtml = "Target - 14030 :<br>";
                subcategories.forEach(sub => {
                    tooltipHtml += `<span style='color: ${subcategoryColor(sub.category)}; font-size:8px;'>●</span> ${sub.category} (${sub.value})<br>`;
                });

                tooltip.html(tooltipHtml)
                    .style("opacity", 1)
                    // .style("left", `${x + 10}px`)
                    // .style("top", `${y + 10}px`);
                    .style("left", `${x + 10}px`)
                    .style("top", `${y - 200}px`);
            } else {
                const tooltipText = `${d.data.category}: ${d.data.value}`;
                tooltip.html(tooltipText)
                    .style("opacity", 0.9)
                    .style("left", `${x + 10}px`)
                    .style("top", `${y + 10}px`);
            }
        })
        .on("mouseout", function () {
            g.selectAll(".nested-arc").remove();
            tooltip.style("opacity", 0);
        });
}

// Call the createPieChart function to generate the chart
// createPieChart_Proteins();

createPieChart_Drugs();
createPieChart_ATClevel1();
createPieChart_Mutations();