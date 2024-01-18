function createBarChartForATCDiseaseClass(disease_classes, disease_class_count)
{
    alert("yang yang yang yang yang");
    const data = [];
    for (var i=0; i<disease_classes.length; i++){
        temp = {
          name: disease_classes[i],
          value: disease_class_count[i],
        }
        data.push(temp);
    }
      
    const margin = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 300, // add more white space on the left side of the visualization to display the names
      };
      
    const width = 800 - (margin.left + margin.right);
    const height = 350 - (margin.top + margin.bottom);
    
    const svg = d3
    .select('#chart-container-ATC-disease-class')
    .html("")
    .append('svg')
    .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`)
    .attr('width', width)
    .attr('height', height);
    
    const group = svg
    .append('g')
    .attr('transform', `translate(${margin.left} -${margin.top})`);
    
    // describe a quantitative scale for the x axis, for the racers' points
    const xScale = d3
    .scaleLinear()
    .domain([0, d3.max(data, ({ value }) => value)])
    .range([0, width]);
    
    // describe a qualitative scale for the y axis, for the racers' names
    const yScale = d3
    .scaleBand()
    .domain(data.map(({ name }) => name))
    .range([0, height])
    // padding allows to separate the shapes making use of the scale and the value returned by the yScale.bandwidth() function
    // 0.2 means 20% is dedicated to white space around the band
    .padding(0.2);
    
    
    // add axes describing the values
    const xAxis = d3
    .axisBottom(xScale);
    
    const yAxis = d3
    .axisLeft(yScale);
    
    group
    .append('g')
    .attr('transform', `translate(0 ${height})`)
    .call(xAxis);
    
    group
    .append('g')
    .call(yAxis)
    .style('font-size', '19px');
    
    // include a group element for each data point, to nest connected elements
    const groups = group
    .selectAll('g.group')
    .data(data, ({ name }) => name)
    .enter()
    .append('g')
    .attr('class', 'group')
    // translate the group vertically according to the y scale
    .attr('transform', ({ name }) => `translate(0 ${yScale(name)})`);
    
    // for each data point add a rectangle describing the points awarded to the respective racer
    groups
    .append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .style("fill", "violet") // add more colors here
    .attr('width', ({ value }) => xScale(value))
    .attr('height', yScale.bandwidth());
}

//------------------------
function createPieChartForATCClinicalTrialPhase(data) {
    const container = document.getElementById("chart-container-ATC-interaction-type");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-ATC-clinical-trial-phase")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    // const color = d3.scaleOrdinal(colors);
    const colors = ["steelblue", "purple", "cyan", "magenta"];
    const color = d3.scaleOrdinal(colors);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-ATC-clinical-trial-phase")
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

//-----------------------------------------------
function createPieChartForATCTargetType(data) {
    const container = document.getElementById("chart-container-ATC-interaction-type");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-ATC-interaction-type")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    // const color = d3.scaleOrdinal(colors);
    const colors = ["#ff99c8", "#43bccd", "#f9c80e", "#662e9b"];
    const color = d3.scaleOrdinal(colors);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-ATC-interaction-type")
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
function createPieChartForATCDrugStatus(data) {
    const container = document.getElementById("chart-container-ATC-drug-status");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-ATC-drug-status")
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

    const tooltip = d3.select("#chart-container-ATC-drug-status")
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
function createPieChartForATCDrugType(data) {
    const container = document.getElementById("chart-container-ATC-drug-type");
    const containerWidth =  300;//container.clientWidth;
    const containerHeight = 300; //container.clientHeight;
    const size = Math.min(containerWidth, containerHeight);
    const radius = size / 2;

    const svg = d3.select("#pie-chart-ATC-drug-type")
        .attr("width", "100%") // Set the SVG width to 100%
        .attr("height", "100%") // Set the SVG height to 100%
        .attr("viewBox", `0 0 ${size} ${size}`) // Use viewBox to control the aspect ratio, ensure the SVG scales properly within the container

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(radius - 60)
        .outerRadius(radius - 10);

    // const colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length);
    const colors = ["#d62828", "#004e98"];
    const color = d3.scaleOrdinal(colors);

    const g = svg.append("g")
        .attr("transform", `translate(${size / 2},${size / 2})`); // Center the chart

    const arcs = g.selectAll(".arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

    const tooltip = d3.select("#chart-container-ATC-drug-type")
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

