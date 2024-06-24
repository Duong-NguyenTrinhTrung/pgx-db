function reset(){
    $("#result-compare-table").html("");
    $("#result-compare-area-text").html("");
    // $("#atc_code_box").html("");
    // $("#atc_comparison_box").html("");
    var plottingAtcCodeBox = document.getElementById("atc_code_box");
    plottingAtcCodeBox.style.width = '50%';
    var plottingAtcComparisonBox = document.getElementById("atc_comparison_box");
    plottingAtcComparisonBox.style.width = '50%';
}

function getLimitedTicks(integerTicks, maxTicks = 10) {
    const tickCount = integerTicks.length;
    if (tickCount <= maxTicks) {
        // If there are 10 or fewer ticks, return the original array
        return integerTicks;
    } else {
        // Calculate the interval at which to pick ticks
        const interval = Math.floor(tickCount / maxTicks);
        const limitedTicks = [];
        for (let i = 0; i < tickCount; i += interval) {
            limitedTicks.push(integerTicks[i]);
        }
        // Ensure the last element is always included
        if (limitedTicks[limitedTicks.length - 1] !== integerTicks[tickCount - 1]) {
            limitedTicks.push(integerTicks[tickCount - 1]);
        }
        return limitedTicks;
    }
}

function createHistogramPlot(data, elementID, text){
    reset();
    // target the .viz container
    const viz = d3.select('#'+elementID).html("");

    // in a header include preliminary information about the project
    const header = viz.append('header');
    header
    .append('h4')
    .style('text-align', 'center')
    .html(text);

    // have the visualizations share the same margin, width and height
    const margin = {
    top: 30,
    right: 20,
    bottom: 60,
    left: 50,
    };
    const width = 500 - (margin.left + margin.right);
    const height = 500 - (margin.top + margin.bottom);

    // HISTOGRAM
    const svgHistogram = viz
    .append('svg')
    .attr('class', 'histogram')
    .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`);

    // linear gradient described for the entire visualization
    // the idea is to have lighter colors toward the top of the svg
    const linearGradient = svgHistogram
    .append('defs')
    .append('linearGradient')
    .attr('id', 'gradient-histogram')
    .attr('gradientUnits', 'userSpaceOnUse')
    .attr('x1', 0)
    .attr('x2', 0)
    .attr('y1', 0)
    .attr('y2', height);

    linearGradient
    .append('stop')
    .attr('stop-color', '#3f37c9')
    .attr('offset', 0);

    linearGradient
    .append('stop')
    .attr('stop-color', '#4cc9f0')
    .attr('offset', 1);

    const groupHistogram = svgHistogram
    .append('g')
    .attr('transform', `translate(${margin.left} ${margin.top})`);

    // for the horizontal dimension the scale is defined for both the histogram and the density plot
    // ! the function is also used by the histogram function to determine the different bins
    const xScale = d3
    .scaleLinear()
    .domain([Math.floor(d3.min(data)), Math.ceil(d3.max(data))])
    .range([0, width]);

    // histogram used to create the bins from the input data
    const histogram = d3
    .histogram()
    .domain(xScale.domain());

    // multi dimensional array describing for each bin the start and end coordinate on the x axis (x0, x1) as well as the data points falling in the bin
    // the number of data points is given by the length of each array
    const dataHistogram = histogram(data);

    // for the vertical dimension, the histogram uses the number of observations
    const yScaleHistogram = d3
    .scaleLinear()
    .domain([0, d3.max(dataHistogram, ({ length }) => length)])
    .range([height, 0]);

    // draw the y axis before the visualization, to have the grid lines behind the histogram' rectangles
    const yAxisHistogram = d3
    .axisLeft(yScaleHistogram);

    // give a class to the axis to later identify and style the elements
    groupHistogram
    .append('g')
    .attr('class', 'axis y-axis')
    .call(yAxisHistogram);

    // Add y-axis label
    groupHistogram
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -margin.left + 10)
        .attr('x', -height / 2)
        .attr('dy', '1em')
        .attr('font-size', '12px')
        .attr('fill', 'currentColor')
        .attr('text-anchor', 'middle')
        .text('Count');

    // HISTOGRAM ELEMENTS
    // add one group for each bin
    const binsHistogram = groupHistogram
    .selectAll('g.bin')
    .data(dataHistogram)
    .enter()
    .append('g')
    .attr('class', 'bin')
    // translate the bins horizontally according to where each bin ought to start
    .attr('transform', ({ x0 }) => `translate(${xScale(x0)} 0)`);

    // in the group elements add a rectangle using the vertical scale
    binsHistogram
    .append('rect')
    .attr('x', 0)
    .attr('y', d => yScaleHistogram(d.length))
    .attr('width', ({ x0, x1 }) => xScale(x1) - xScale(x0))
    .attr('height', d => height - yScaleHistogram(d.length))
    .attr('fill', 'url(#gradient-histogram)')
    // .attr('stroke', 'white')
    // .attr('stroke-width', 2);

    // at the top of the rectangles include a text describing the precise count
    binsHistogram
    .append('text')
    .attr('x', ({ x0, x1 }) => (xScale(x1) - xScale(x0)) / 2)
    .attr('y', d => yScaleHistogram(d.length) - margin.top / 3)
    .attr('fill', 'url(#gradient-histogram)')
    .attr('text-anchor', 'middle')
    .attr('font-weight', 'bold')
    .attr('font-size', '1.1rem')
    .text(d => d.length);

    // draw the y axis on top of the rectangles
    const xAxis = d3
    .axisBottom(xScale)
    .tickPadding(10);

    groupHistogram
    .append('g')
    .attr('class', 'axis x-axis')
    .attr('transform', `translate(0 ${height})`)
    .call(xAxis);

    // style the axes of both visualizations
    // remove all line elements
    d3
    .selectAll('.axis')
    .selectAll('line')
    .remove();

    // for the horizontal axis, increase the size of the labels and include a label beneath the values
    d3
    .selectAll('.x-axis')
    .append('text')
    .attr('x', width / 2)
    .attr('y', margin.bottom-5)
    .attr('font-size', '12px')
    .attr('fill', 'currentColor')
    .text('Degree of connection');

    // for the vertical dimension, add the axes, but hide the content it in favor of grid lines
    d3
    .selectAll('.y-axis')
    .selectAll('path')
    .remove();
    d3
    .selectAll('.y-axis')
    .selectAll('text')
    .remove();

    d3
    .selectAll('.y-axis')
    .selectAll('g.tick')
    .append('path')
    .attr('d', `M 0 0 h ${width}`)
    .attr('stroke', 'currentColor')
    .attr('stroke-width', 1)
    .attr('opacity', 0.25);
}
function createDistributionPlot(data, elementID, text) {
    reset();
    if (data.length>0){
        const viz = d3.select('#' + elementID)
            .html("");
        const margin = {
            top: 30,
            right: 20,
            bottom: 50,
            left: 20,
        };
        const width = 500 - (margin.left + margin.right);
        const height = 500 - (margin.top + margin.bottom);
    
        const header = viz.append('header').style('text-align', 'center');
        header
            .append('h4')
            .html(text);
    
        const svgHistogram = viz
            .append('svg')
            .attr('class', 'histogram')
            .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`);
    
        const groupHistogram = svgHistogram
            .append('g')
            .attr('transform', `translate(${margin.left+10}  ${margin.top})`);
    
        const xScale = d3
            .scaleLinear()
            .domain([d3.min(data), d3.max(data)])
            .range([0, width]);
    
        const maxValue = d3.max(data);
        const integerTicks = d3.range(1, maxValue + 1); 
    
        const histogram = d3
            .histogram()
            .domain(xScale.domain());
    
        const dataHistogram = histogram(data);
        const dataHistogramAll = histogram(data);
    
        const yScaleHistogram = d3
            .scaleLinear()
            .domain([0, d3.max(dataHistogramAll, ({ length }) => length)])
            .range([height, 0]);
    
        const yAxisHistogram = d3
            .axisLeft(yScaleHistogram)
            .tickFormat(d3.format('d'))
            .tickValues(d3.ticks(yScaleHistogram.domain()[0], yScaleHistogram.domain()[1], Math.ceil(yScaleHistogram.domain()[1])));
        ;
        groupHistogram
            .append('g')
            .attr('class', 'axis y-axis')
            .call(yAxisHistogram)
            .attr('transform', `translate(0 20)`);
    
        const binsHistogram = groupHistogram
            .selectAll('g.bin')
            .data(dataHistogram)
            .enter()
            .append('g')
            .attr('class', 'bin')
            .attr('transform', ({ x0 }) => `translate(${xScale(x0)} 0)`);
    
        binsHistogram
            .append('rect')
            .attr('x', 0)
            .attr('y', d => yScaleHistogram(d.length) + 20)
            .attr('width', ({ x0, x1 }) => xScale(x1) - xScale(x0))
            .attr('height', d => height - yScaleHistogram(d.length))
            .attr('fill', '#4cc9f0') 
            .attr('stroke', 'white')
            .attr('stroke-width', 1);
    
        binsHistogram
            .append('text')
            .attr('x', ({ x0, x1 }) => (xScale(x1) - xScale(x0)) / 2)
            .attr('y', d => yScaleHistogram(d.length) - margin.top / 3 + 25)
            .attr('fill', 'grey')
            .attr('text-anchor', 'middle')
            .attr('font-weight', 'bold')
            .attr('font-size', '1.1rem')
            .text(d => d.length);
    
        const limitedIntegerTicks = getLimitedTicks(integerTicks);
    
        const xAxis = d3
            .axisBottom(xScale)
            .tickPadding(10)
            .tickFormat(d3.format('d'))
            .tickValues(limitedIntegerTicks);
    
        const xAxisGroup = groupHistogram
            .append('g')
            .attr('class', 'axis x-axis')
            .attr('transform', `translate(0 ${height + 20})`)
            .call(xAxis)
            .attr('font-size', '10px');

        // Rotate x-tick labels if they have more than 2 digits
        xAxisGroup.selectAll("text")
            .attr("transform", function() {
                return this.innerHTML.length > 2 ? "rotate(-45)" : "rotate(0)";
            })
            .style("text-anchor", function() {
                return this.innerHTML.length > 2 ? "end" : "middle";
            })
            .attr("dx", function() {
                return this.innerHTML.length > 2 ? "-0.8em" : "0";
            })
            .attr("dy", function() {
                return this.innerHTML.length > 2 ? "0.15em" : "0.71em";
            });
        

    }else{
        const viz = d3.select('#' + elementID)
            .html("");
        const header = viz.append('header').style('text-align', 'center');
        header
            .append('h4').html(text)
            .append('h5')
            .style('color', 'red')
            .html("No connections");
        }
}

// 2 plots sharing a-xis
// function createDistributionPlot2(dataAtcCode, dataAtcComparison, atc_code, atc_comparison, elementID1, elementID2, text) {
//     reset();
//     var plottingBox1 = document.getElementById(elementID1);
//     plottingBox1.style.width = '100%';
//     var plottingBox2 = document.getElementById(elementID2);
//     plottingBox2.style.width = '0';
//     var value1 = [];
//     var value2 = [];

//     const viz = d3.select('#' + elementID1)
//         .html("");
//     const margin = {
//         top: 30,
//         right: 20,
//         bottom: 50,
//         left: 20,
//     };
//     const width = 500 - (margin.left + margin.right);
//     const height = 500 - (margin.top + margin.bottom);

//     const header = viz.append('header').style('text-align', 'center');
//     header
//         .append('h4')
//         .html(text);

//     const svgHistogram = viz
//         .append('svg')
//         .attr('class', 'histogram')
//         .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`);

//     const groupHistogram = svgHistogram
//         .append('g')
//         .attr('transform', `translate(${margin.left}  ${margin.top})`);

//     const xScale = d3
//         .scaleLinear()
//         .domain([d3.min(dataAtcCode.concat(dataAtcComparison)), d3.max(dataAtcCode.concat(dataAtcComparison))])
//         .range([0, width]);

//     // const maxValue = d3.max(data_all);
//     // const integerTicks = d3.range(0, maxValue + 1); 

//     const histogram = d3
//         .histogram()
//         .domain(xScale.domain())
//         .thresholds(xScale.ticks(20));
    
//     const dataHistogramAtcCode = histogram(dataAtcCode);
//     const dataHistogramAtcComparison = histogram(dataAtcComparison);


//     const yScaleHistogram = d3
//         .scaleLinear()
//         .domain([0, d3.max(dataHistogramAtcCode.concat(dataHistogramAtcComparison), ({ length }) => length)])
//         .range([height, 0]);

//     const yAxisHistogram = d3
//         .axisLeft(yScaleHistogram)
//         .tickFormat(d3.format('d'))
//         .tickValues(d3.ticks(yScaleHistogram.domain()[0], yScaleHistogram.domain()[1], Math.ceil(yScaleHistogram.domain()[1])));
    
//     groupHistogram
//         .append('g')
//         .attr('class', 'axis y-axis')
//         .call(yAxisHistogram)
//         .attr('transform', `translate(0 0)`);

//     const binsAtcCode = groupHistogram
//         .selectAll('g.bin.atc_code')
//         .data(dataHistogramAtcCode)
//         .enter()
//         .append('g')
//         .attr('class', 'bin atc_code')
//         .attr('transform', ({ x0 }) => `translate(${xScale(x0)} 0)`);
    
//         binsAtcCode
//         .append('rect')
//         .attr('x', 0)
//         .attr('y', d => yScaleHistogram(d.length))
//         .attr('width', ({ x0, x1 }) => xScale(x1) - xScale(x0))
//         .attr('height', d => height - yScaleHistogram(d.length))
//         .attr('fill', '#4cc9f0')
//         .attr('stroke', 'white')
//         .attr('stroke-width', 1);

//     binsAtcCode
//         .append('text')
//         .attr('x', ({ x0, x1 }) => (xScale(x1) - xScale(x0)) / 2)
//         .attr('y', d => yScaleHistogram(d.length) - 5)
//         .attr('fill', 'grey')
//         .attr('text-anchor', 'middle')
//         .attr('font-weight', 'bold')
//         .attr('font-size', '1.1rem')
//         .text(d => d.length);

//         const binsAtcComparison = groupHistogram
//         .selectAll('g.bin.atc_comparison')
//         .data(dataHistogramAtcComparison)
//         .enter()
//         .append('g')
//         .attr('class', 'bin atc_comparison')
//         .attr('transform', ({ x0 }) => `translate(${xScale(x0)} 0)`);

//     binsAtcComparison
//         .append('rect')
//         .attr('x', 0)
//         .attr('y', d => yScaleHistogram(d.length))
//         .attr('width', ({ x0, x1 }) => xScale(x1) - xScale(x0))
//         .attr('height', d => height - yScaleHistogram(d.length))
//         .attr('fill', '#f72585')
//         .attr('stroke', 'white')
//         .attr('stroke-width', 1);

//     binsAtcComparison
//         .append('text')
//         .attr('x', ({ x0, x1 }) => (xScale(x1) - xScale(x0)) / 2)
//         .attr('y', d => yScaleHistogram(d.length) - 5)
//         .attr('fill', 'grey')
//         .attr('text-anchor', 'middle')
//         .attr('font-weight', 'bold')
//         .attr('font-size', '1.1rem')
//         .text(d => d.length);
    
//     const maxValue = Math.max(d3.max(dataAtcCode), d3.max(dataAtcComparison));
//     const integerTicks = d3.range(0, maxValue + 1);
//     const limitedIntegerTicks = getLimitedTicks(integerTicks);

//     const xAxis = d3
//         .axisBottom(xScale)
//         .tickPadding(10)
//         .tickFormat(d3.format('d'))
//         .tickValues(limitedIntegerTicks);

//     const xAxisGroup =groupHistogram
//         .append('g')
//         .attr('class', 'axis x-axis')
//         .attr('transform', `translate(0 ${height})`)
//         .call(xAxis)
//         .attr('font-size', '10px');

//     // Rotate x-tick labels if they have more than 2 digits
//     xAxisGroup.selectAll("text")
//     .attr("transform", function () {
//         return this.innerHTML.length > 2 ? "rotate(-45)" : "rotate(0)";
//     })
//     .style("text-anchor", function () {
//         return this.innerHTML.length > 2 ? "end" : "middle";
//     })
//     .attr("dx", function () {
//         return this.innerHTML.length > 2 ? "-0.8em" : "0";
//     })
//     .attr("dy", function () {
//         return this.innerHTML.length > 2 ? "0.15em" : "0.71em";
//     });

//     // Add legend
//     const legend = svgHistogram.append('g')
//     .attr('class', 'legend')
//     .attr('transform', `translate(${margin.left}, ${margin.top - 20})`);

//     legend.append('rect')
//         .attr('x', 0)
//         .attr('y', 0)
//         .attr('width', 18)
//         .attr('height', 18)
//         .style('fill', '#4cc9f0');

//     legend.append('text')
//         .attr('x', 24)
//         .attr('y', 9)
//         .attr('dy', '.35em')
//         .style('text-anchor', 'start')
//         .text(atc_code);

//     legend.append('rect')
//         .attr('x', 0)
//         .attr('y', 20)
//         .attr('width', 18)
//         .attr('height', 18)
//         .style('fill', '#f72585');

//     legend.append('text')
//         .attr('x', 24)
//         .attr('y', 29)
//         .attr('dy', '.35em')
//         .style('text-anchor', 'start')
//         .text(atc_comparison);
    
// }

function toTitleCase(str) {
    return str.toLowerCase().split(' ').map(word => {
        return word.charAt(0).toUpperCase() + word.slice(1);
    }).join(' ');
}

function createDistributionPlotForCategoryData(classes, class_count, elementID, text, relation) {
    var types;
    if (relation==="interactions"){
        types = "Modes of action"
    }else{
        types = "Clinical trial phases";
    }
    reset();
    if (classes.length>0)
    {
        const data = [];
        for (var i = 0; i < classes.length; i++) {
            temp = {
                name: toTitleCase(classes[i]),
                value: class_count[i],
            }
            data.push(temp);
        }
        const margin = {
            top: 20,
            right: 20,
            bottom: 20,
            left: 300, 
        };

        const width = 800 - (margin.left + margin.right);
        const height = 350 - (margin.top + margin.bottom);

        const viz = d3.select('#' + elementID).html("");
        const header = viz.append('header').style('text-align', 'center').style("color", "#3498db");
        header.append('h4').html(text);

        const svg = viz
            .append('svg')
            .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`)
            .attr('width', width)
            .attr('height', height);

        const group = svg
            .append('g')
            .attr('transform', `translate(${margin.left} -${margin.top})`);

        const xScale = d3
            .scaleLinear()
            .domain([0, d3.max(data, ({ value }) => value)])
            .range([0, width]);

        const maxValue = d3.max(data, ({ value }) => value);
        const tickCount = Math.min(maxValue, 10); // Ensure we have at most 10 ticks
        const integerTicks = d3.ticks(0, maxValue, tickCount); // Generate up to 10 ticks

        const xAxis = d3.axisBottom(xScale)
            .tickValues(integerTicks) // Use the generated array of integers for tick values
            .tickFormat(d3.format('d')); // Ensure the format is set to integers

        // describe a qualitative scale for the y axis, for the racers' names
        const yScale = d3
            .scaleBand()
            .domain(data.map(({ name }) => name))
            .range([0, height])
            // padding allows to separate the shapes making use of the scale and the value returned by the yScale.bandwidth() function
            // 0.2 means 20% is dedicated to white space around the band
            .padding(0.2);

        const yAxis = d3
            .axisLeft(yScale);

        group
            .append('g')
            .attr('transform', `translate(0 ${height})`)
            .call(xAxis)
            .style('font-size', '17px');

        group
            .append('g')
            .call(yAxis)
            .style('font-size', '19px');

        // Add x-axis label
        svg.append('text')
        .attr('class', 'x-axis-label')
        .attr('text-anchor', 'middle')
        .attr('x', width / 2 + margin.left)
        .attr('y', height + margin.top + 40) // Adjust the value as necessary for spacing
        .style('font-size', '18px')
        .text('No. of '+relation); // Replace with your actual label

        // Add y-axis label
        // svg.append('text')
        // .attr('class', 'y-axis-label')
        // .attr('text-anchor', 'middle')
        // .attr('transform', 'rotate(-90)')
        // .attr('x', -height / 2 - margin.top)
        // .attr('y', margin.left - 60) // Adjust the value as necessary for spacing
        // .style('font-size', '16px')
        // .text(types); // Replace with your actual label

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
            .style("fill", d3.scaleOrdinal(d3.schemeSet3)) // add more colors here
            .attr('width', ({ value }) => xScale(value))
            .attr('height', yScale.bandwidth());
    }else{
            console.log(text + " no plot");
            const viz = d3.select('#' + elementID).html("");
            const header = viz.append('header').style('text-align', 'center').style("color", "#3498db");
            header.append('h4').html(text).append('h5').html("There is no "+relation).style("color", "red");
        }
}

function createDistributionPlotForCategoryData2(atc_code, classes1, class_count1, atc_comparison, classes2, class_count2, elementID1, elementID2, text, relation) {
    reset();
    var value1 = [];
    var value2 = [];
    var plottingBox1 = document.getElementById(elementID1);
    plottingBox1.style.width = '100%';
    var plottingBox2 = document.getElementById(elementID2);
    plottingBox2.style.width = '0';
    const combinedArray = [...classes1, ...classes2];
    const unionSet = new Set(combinedArray);

    for (let value of unionSet) {
        if (classes1.includes(value)) {
            var index = classes1.indexOf(value);
            value1.push({
                grpName: toTitleCase(value),
                grpValue: class_count1[index],
            });
        } else {
            value1.push({
                grpName: toTitleCase(value),
                grpValue: 0,
            });
        }
        if (classes2.includes(value)) {
            var index = classes2.indexOf(value);
            value2.push({
                grpName: toTitleCase(value),
                grpValue: class_count2[index],
            });
        } else {
            value2.push({
                grpName: toTitleCase(value),
                grpValue: 0,
            });
        }
    }
    const groupData = [
        {
            key: atc_code, values: value1
        },
        {
            key: atc_comparison, values: value2
        },
    ];
    var margin = { top: 20, right: 20, bottom: 30, left: 60 };
    var width = (plottingBox1.clientWidth - margin.left - margin.right -70);
    var height = 400 - margin.top - margin.bottom;

    var x0 = d3.scaleBand()
        .rangeRound([0, width-60], .5)
        .paddingInner(0.1);

    var x1 = d3.scaleBand();
    var y = d3.scaleLinear().rangeRound([height, 0]);

    var xAxis = d3.axisBottom().scale(x0)
        .tickValues(groupData.map(d => d.key));

    var yAxis = d3.axisLeft().scale(y);
    const color = d3.scaleOrdinal(d3.schemeSet3);

    const viz = d3.select('#' + elementID1).html("");
    const header = viz.append('header').style('text-align', 'center').style("color", "#3498db");
    header.append('h4').html(text);

    var svg = viz.append('svg')
        .attr('width', width + margin.left + margin.right +70)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    var categories = groupData.map(function (d) { return d.key; });
    var counts = groupData[0].values.map(function (d) { return d.grpName; });

    x0.domain(categories);
    x1.domain(counts).rangeRound([0, x0.bandwidth()]);
    y.domain([0, d3.max(groupData, function (key) { return d3.max(key.values, function (d) { return d.grpValue; }); })]);

    svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

    svg.selectAll('.x.axis text')
        .style('font-size', '14px')
        .style('fill', 'red');

    svg.append('g')
        .attr('class', 'y axis')
        .style('opacity', '0')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .style('font-weight', 'bold')
        .text('Value');
    
    // Add y-axis label
    svg.append('text')
    .attr('class', 'y-axis-label')
    .attr('text-anchor', 'middle')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2 - margin.top)
    .attr('y', -margin.left + 20) 
    .style('font-size', '14px')
    .text("No. of "+relation); 

    svg.select('.y').transition().duration(500).delay(1300).style('opacity', '1');

    var slice = svg.selectAll('.slice')
        .data(groupData)
        .enter().append('g')
        .attr('class', 'g')
        .attr('id', function (d, i) {
            console.log("data: " + d);
            console.log("i: " + i);
            return `atc-${i}`;
        })
        .attr('transform', function (d) { return 'translate(' + x0(d.key) + ',0)'; });

    slice.selectAll('rect')
        .data(function (d) { return d.values; })
        .enter().append('rect')
        .attr('width', x1.bandwidth())
        .attr('x', function (d, i) { console.log("index: " + i); return x1(d.grpName); })
        .attr('id', function (d, i) {
            return `col-${i}`;
        })
        .style('fill', function (d) { return color(d.grpName) })
        .attr('y', function (d) { return y(0); })
        .attr('height', function (d) { return height - y(0); })
        .on('mouseover', function (event, d) {
            d3.select(this).style('fill', d3.color(color(d.grpName)).darker(1));

            svg.append('text')
                .attr('class', 'nw_comparison_tooltip')
                .attr('x', parseInt(event.target.parentElement.getAttribute("id").replace("atc-", "")) * (parseInt(event.target.getAttribute("id").replace("col-", "")) + 1) * parseInt(event.target.getAttribute("width")) + d3.pointer(event)[0])   
                .attr('x', parseInt(d3.pointer(event, this)[0]) + 10)   // Positioning the text
                .attr('y', parseInt(d3.pointer(event, this)[1]) - 10)
                .attr('dy', '.35em')
                .attr('text-anchor', 'start')
                .style('font-size', '12px')
                .style('font-family', 'sans-serif')
                .style('fill', 'black')
                .style('background-color', 'white')
                .style('pointer-events', 'none') // Ensure the tooltip does not interfere with mouse events
                .text(d.grpValue);
        })
        .on('mouseout', function (event, d) {
            d3.select(this).style('fill', d3.color(color(d.grpName)));
            svg.selectAll('.nw_comparison_tooltip').remove();
        })
        .on('mousemove', function (event, d) {
            d3.select('.nw_comparison_tooltip')
                .attr('x', function () {
                    return parseInt(d3.pointer(event, this )[0]) + 10;
                }) // Positioning the text
                .attr('y', parseInt(d3.pointer(event, this )[1]) - 10)
        });

    slice.selectAll('rect')
        .transition()
        .delay(function (d) { return Math.random() * 1000; })
        .duration(1000)
        .attr('y', function (d) { return y(d.grpValue); })
        .attr('height', function (d) { return height - y(d.grpValue); });

    // Legend
    var legend = svg.selectAll('.legend')
        .data(groupData[0].values.map(function (d) { return toTitleCase(d.grpName); }).reverse())
        .enter().append('g')
        .attr('class', 'legend')
        .attr('transform', function (d, i) { return 'translate(' + (width + margin.left + margin.right - 35) + ',' + i * 20 + ')'; })  // Adjusted x position
        .style('opacity', '0');

    legend.append('rect')
        .attr('x', 0)  // Adjusted x position to keep the rectangles aligned
        .attr('width', 18)
        .attr('height', 18)
        .style('fill', function (d) { return color(d); });

    legend.append('text')
        .attr('x', -6)  // Adjusted x position to keep the text aligned
        .attr('y', 9)
        .attr('dy', '.35em')
        .style('text-anchor', 'end')
        .text(function (d) { return d; });
    legend.transition().duration(500).delay(function (d, i) { return 1300 + 100 * i; }).style('opacity', '1');
}


function compareNetworkSize(dataAtcCode, dataAtcComparison, elementID, text) {
    reset();
    $("#atc_code_box").html("");
    $("#atc_comparison_box").html("");
    $("#result-compare-table").css("width", "40%");
    $("#result-compare-area-text").html(`${text}`);
    $("#result-compare-area-text").css("color", "#3498db");
    var htmlData = `<table><thead><tr style="color: #d90429"><th>Atc code</th><th>${dataAtcCode.name_atc_code}</th><th>${dataAtcComparison.name_atc_code}</th></tr></thead><tbody>`;
    htmlData += `<tr><td>No. of drugs</td><td>${dataAtcCode.no_of_drugs}</td><td>${dataAtcComparison.no_of_drugs}</td></tr>`;
    htmlData += `<tr><td>No. of diseases</td><td>${dataAtcCode.no_of_diseases}</td><td>${dataAtcComparison.no_of_diseases}</td></tr>`;
    htmlData += `<tr><td>No. of proteins</td><td>${dataAtcCode.no_of_proteins}</td><td>${dataAtcComparison.no_of_proteins}</td></tr>`;
    htmlData += `<tr><td>No. of drug-protein interactions</td><td>${dataAtcCode.NoOfDrugPoteinInteractions}</td><td>${dataAtcComparison.NoOfDrugPoteinInteractions}</td></tr>`;
    htmlData += `<tr><td>No. of drug-disease associations</td><td>${dataAtcCode.NoOfDrugDiseaseAssociationStudy}</td><td>${dataAtcComparison.NoOfDrugDiseaseAssociationStudy}</td></tr></tbody></table>`;
    $("#" + elementID).html(htmlData);
}

function measureCentralizationDrugDisease(data, elementID, text) {
    reset();

    var degreeCentralityDrugData = data["degree_centrality_drug"];
    var betweennessCentralityDrugData = data["betweenness_centrality_drug"];
    var degreeCentralityDiseaseData = data["degree_centrality_disease"];
    var betweennessCentralityDiseaseData = data["betweenness_centrality_disease"];

    var e = $("#" + elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable = `<table><tbody><tr><td colspan="3" style="color: #d90429;font-weight: bold;">Centrality of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < degreeCentralityDrugData.length; i++) {
        var drugObject = degreeCentralityDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var degreeValue = drugObject[drugName];
        var betweennessObject = betweennessCentralityDrugData[i];
        var betweennessValue = betweennessObject[drugName]; // Assuming drug names are the same in both datasets
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${degreeValue.toFixed(2)}</td><td>&nbsp;&nbsp;${betweennessValue.toFixed(2)}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="3" style="color: #d90429; font-weight: bold;">Centrality of disease nodes</td></tr>

    <tr style="color: #3498db; font-weight: bold;"><td>Disease name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < degreeCentralityDiseaseData.length; i++) {
        var diseaseObject = degreeCentralityDiseaseData[i];
        var diseaseName = Object.keys(diseaseObject)[0];
        var degreeValue = diseaseObject[diseaseName];
        var betweennessObject = betweennessCentralityDiseaseData[i];
        var betweennessValue = betweennessObject[diseaseName]; // Assuming disease names are the same in both datasets
        htmlTable += `<tr><td>&nbsp;&nbsp;${diseaseName.slice(1)}</td><td>&nbsp;&nbsp;${degreeValue.toFixed(2)}</td><td>&nbsp;&nbsp;${betweennessValue.toFixed(2)}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}

function measureCentralizationDrugProtein(data, elementID, text) {
    reset();

    var degreeCentralityDrugData = data["degree_centrality_drug"];
    var betweennessCentralityDrugData = data["betweenness_centrality_drug"];
    var degreeCentralityGeneData = data["degree_centrality_gene"];
    var betweennessCentralityGeneData = data["betweenness_centrality_gene"];

    var e = $("#" + elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable = `<table><tbody><tr><td colspan="3" style="color: #d90429;font-weight: bold;">Centrality of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < degreeCentralityDrugData.length; i++) {
        var drugObject = degreeCentralityDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var degreeValue = drugObject[drugName];
        var betweennessObject = betweennessCentralityDrugData[i];
        var betweennessValue = betweennessObject[drugName]; // Assuming drug names are the same in both datasets
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${degreeValue.toFixed(2)}</td><td>&nbsp;&nbsp;${betweennessValue.toFixed(2)}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="3" style="color: #d90429; font-weight: bold;">Centrality of protein <i>(in genename)</i> nodes</td></tr>

    <tr style="color: #3498db; font-weight: bold;"><td>Gene name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < degreeCentralityGeneData.length; i++) {
        var geneObject = degreeCentralityGeneData[i];
        var geneName = Object.keys(geneObject)[0];
        var degreeValue = geneObject[geneName];
        var betweennessObject = betweennessCentralityGeneData[i];
        var betweennessValue = betweennessObject[geneName]; // Assuming disease names are the same in both datasets
        htmlTable += `<tr><td>&nbsp;&nbsp;${geneName.slice(1)}</td><td>&nbsp;&nbsp;${degreeValue.toFixed(2)}</td><td>&nbsp;&nbsp;${betweennessValue.toFixed(2)}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}

function detectingCommunityDrugDisease(data, elementID, text) {
    reset();

    var partitionDrugData = data["partition_drug"];
    var partitionDiseaseData = data["partition_disease"];

    console.log("partitionDrugData: " + partitionDrugData);
    console.log("partitionDiseaseData: " + partitionDiseaseData);

    var e = $("#" + elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable = `<table><tbody><tr><td colspan="2" style="color: #d90429;font-weight: bold;">Community of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < partitionDrugData.length; i++) {
        var drugObject = partitionDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var communityValue = drugObject[drugName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="2" style="color: #d90429; font-weight: bold;">Community of disease nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Disease name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < partitionDiseaseData.length; i++) {
        var diseaseObject = partitionDiseaseData[i];
        var diseaseName = Object.keys(diseaseObject)[0];
        var communityValue = diseaseObject[diseaseName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${diseaseName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}

function detectingCommunityDrugProtein(data, elementID, text) {
    reset();

    var partitionDrugData = data["partition_drug"];
    var partitionGeneData = data["partition_gene"];

    var e = $("#" + elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable = `<table><tbody><tr><td colspan="2" style="color: #d90429;font-weight: bold;">Community of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < partitionDrugData.length; i++) {
        var drugObject = partitionDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var communityValue = drugObject[drugName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="2" style="color: #d90429; font-weight: bold;">Community of protein <i>(in genename)</i> nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Gene name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for (var i = 0; i < partitionGeneData.length; i++) {
        var geneObject = partitionGeneData[i];
        var geneName = Object.keys(geneObject)[0];
        var communityValue = geneObject[geneName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${geneName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}



function calculatePathLength(data, elementID, text) {
    reset();
    var no_of_components = data["no_of_components"];
    var component_detail = data["component_detail"];
    var e = $("#" + elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    e.append(`<p>Number of component: <span style="color:#d90429;font-weight: bold;">${no_of_components}</span></p><br>`);

    var htmlTable = `<table><tbody><tr style="color: #3498db;font-weight: bold;"><td>Component</td><td>&nbsp;&nbsp;&nbsp;&nbsp;List of node(s)</td><td>&nbsp;&nbsp;&nbsp;&nbsp;Average path length</td></tr>`;

    // Iterate through the data and build table rows
    for (var i = 0; i < component_detail.length; i++) {
        var nodes = component_detail[i]["nodes"];
        var average_shortest_path_length = component_detail[i]["average_shortest_path_length"];
        htmlTable += `<tr><td>${i + 1}</td><td>&nbsp;&nbsp;&nbsp;&nbsp;${nodes.join('<br>')}</td><td>&nbsp;&nbsp;&nbsp;&nbsp;${average_shortest_path_length.toFixed(2)}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}


function convert(objects) {
    if (objects.length == 0) {
        return "None";
    } else {
        return objects.join(", ");
    }
}
function commonAndUniqueNodes(data, text) {
    reset();
    $("#result-compare-table").css("width", "40%");
    $("#result-compare-area-text").append(`<h4>${text}</h4>`);
    $("#result-compare-area-text").css("color", "#3498db");
    var common_drugs = convert(data.common_drugs);
    var common_proteins = convert(data.common_proteins);
    var common_diseases = convert(data.common_diseases);

    var unique_drug_atc_code = convert(data.unique_drug_atc_code);
    var unique_protein_atc_code = convert(data.unique_protein_atc_code);
    var unique_disease_atc_code = convert(data.unique_disease_atc_code);
    var unique_drug_atc_comparison = convert(data.unique_drug_atc_comparison);
    var unique_protein_atc_comparison = convert(data.unique_protein_atc_comparison);
    var unique_disease_atc_comparison = convert(data.unique_disease_atc_comparison);

    $("#result-compare-area-text").append(`</h6>Common drugs: <span style="color: #d90429">${common_drugs}</span></h6><br>`);
    $("#result-compare-area-text").append(`</h6>Common proteins: <span style="color: #d90429">${common_proteins}</span></h6><br>`);
    $("#result-compare-area-text").append(`</h6>Common disease: <span style="color: #d90429">${common_diseases}</span></h6><br><br>`);

    var htmlData = `<table id="commonUniqueNodesTable"><thead><tr style="color: #d90429; "><th>Atc code</th><th>${data.atc_code}</th><th>${data.atc_comparison}</th></tr></thead><tbody>`;
    htmlData += `<tr><td>Unique drugs</td><td>${unique_drug_atc_code}</td><td>${unique_drug_atc_comparison}</td></tr>`;
    htmlData += `<tr><td>Unique proteins</td><td>${unique_protein_atc_code}</td><td>${unique_protein_atc_comparison}</td></tr>`;
    htmlData += `<tr><td>Unique disease</td><td>${unique_disease_atc_code}</td><td>${unique_disease_atc_comparison}</td></tr>`;
    $("#result-compare-table").html(htmlData);
}

