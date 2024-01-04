function createPieChartForTargetType(data) {
    const container = document.getElementById("chart-container-interaction-type");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-interaction-type")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    const colors = ["#ff99c8", "#43bccd", "#f9c80e", "#662e9b"];
    const color = d3.scaleOrdinal(colors);
   

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-interaction-type")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0); //opacity of 0 (hidden)

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            const newArc = d3.arc()
                .innerRadius(radius -60)
                .outerRadius(radius); 

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
                // .style("left", "50px")
                // .style("top", "50px");
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


// ----------------------- 
function createPieChartForDrugStatus(data) {
    const container = document.getElementById("chart-container-drug-status");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drug-status")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    const colors = ["#ee6055", "#60d394", "#aaf683", "#ffd97d", "#ff9b85", "#e4c1f9"];
    const color = d3.scaleOrdinal(colors);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-drug-status")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0); //opacity of 0 (hidden)

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            const newArc = d3.arc()
                .innerRadius(radius -60)
                .outerRadius(radius); 

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
                // .style("left", "50px")
                // .style("top", "50px");
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


// ----------------------- 
function createPieChartForDrugType(data) {
    const container = document.getElementById("chart-container-drug-type");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-drug-type")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    const colors = ["#d62828", "#003049"];
    const color = d3.scaleOrdinal(colors);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-drug-type")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0); //opacity of 0 (hidden)

    arcs.append("path")
        .attr("d", arc)
        .style("fill", d => color(d.data.category))
        .on("mouseover", function (event, d) {
            const newArc = d3.arc()
                .innerRadius(radius -60)
                .outerRadius(radius); 

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
                // .style("left", "50px")
                // .style("top", "50px");
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

