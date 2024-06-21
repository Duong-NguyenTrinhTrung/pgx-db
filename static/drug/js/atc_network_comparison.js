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

function createDistributionPlot(data, data_all, elementID, text) {
    reset();
    
    // target the .viz container
    const viz = d3.select('#' + elementID)
        .html("");
    // have the visualizations share the same margin, width and height
    const margin = {
        top: 30,
        right: 20,
        bottom: 50,
        left: 20,
    };
    const width = 500 - (margin.left + margin.right);
    const height = 500 - (margin.top + margin.bottom);

    // in a header include preliminary information about the project
    const header = viz.append('header').style('text-align', 'center');
    header
        .append('h4')
        .html(text);

    // Adds an SVG element for the histogram and sets its class and viewBox
    const svgHistogram = viz
        .append('svg')
        .attr('class', 'histogram')
        .attr('viewBox', `0 0 ${width + (margin.left + margin.right)} ${height + (margin.top + margin.bottom)}`);

    //Sets up the group for the histogram, defines the x and y scales, and prepares the data for the histogram.
    const groupHistogram = svgHistogram
        .append('g')
        .attr('transform', `translate(${margin.left}  ${margin.top})`);

    // for the horizontal dimension the scale is defined for both the histogram and the density plot
    // ! the function is also used by the histogram function to determine the different bins
    const xScale = d3
        .scaleLinear()
        .domain([d3.min(data_all), d3.max(data_all)])
        .range([0, width]);

    const maxValue = d3.max(data_all);
    const integerTicks = d3.range(0, maxValue + 1); // +1 to include the maxValue itself


    // histogram used to create the bins from the input data
    const histogram = d3
        .histogram()
        .domain(xScale.domain());

    // multi dimensional array describing for each bin the start and end coordinate on the x axis (x0, x1) as well as the data points falling in the bin
    // the number of data points is given by the length of each array
    const dataHistogram = histogram(data);
    const dataHistogramAll = histogram(data_all);

    // for the vertical dimension, the histogram uses the number of observations
    const yScaleHistogram = d3
        .scaleLinear()
        .domain([0, d3.max(dataHistogramAll, ({ length }) => length)])
        .range([height, 0]);

    // draw the y axis before the visualization, to have the grid lines behind the histogram' rectangles
    const yAxisHistogram = d3
        .axisLeft(yScaleHistogram)
        .tickFormat(d3.format('d'))
        .tickValues(d3.ticks(yScaleHistogram.domain()[0], yScaleHistogram.domain()[1], Math.ceil(yScaleHistogram.domain()[1])));
    ;
    // give a class to the axis to later identify and style the elements
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
        // translate the bins horizontally according to where each bin ought to start
        .attr('transform', ({ x0 }) => `translate(${xScale(x0)} 0)`);

    // in the group elements add a rectangle using the vertical scale
    binsHistogram
        .append('rect')
        .attr('x', 0)
        .attr('y', d => yScaleHistogram(d.length) + 20)
        .attr('width', ({ x0, x1 }) => xScale(x1) - xScale(x0))
        .attr('height', d => height - yScaleHistogram(d.length))
        // .attr('fill', 'url(#gradient-histogram)')
        .attr('fill', '#69b3a2') // Solid fill color for the bars
        .attr('stroke', '#0c1620')
        .attr('stroke-width', 1);

    // at the top of the rectangles include a text describing the precise count
    binsHistogram
        .append('text')
        .attr('x', ({ x0, x1 }) => (xScale(x1) - xScale(x0)) / 2)
        .attr('y', d => yScaleHistogram(d.length) - margin.top / 3 + 25)
        // .attr('fill', 'url(#gradient-histogram)')
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
    // .tickValues(d3.ticks(xScale.domain()[0], xScale.domain()[1], Math.ceil(xScale.domain()[1])));

    groupHistogram
        .append('g')
        .attr('class', 'axis x-axis')
        .attr('transform', `translate(0 ${height + 20})`)
        .call(xAxis)
        .attr('font-size', '10px');
}

function createDistributionPlotForCategoryData(classes, class_count, elementID, text) {
    reset();
    const data = [];
    for (var i = 0; i < classes.length; i++) {
        temp = {
            name: classes[i],
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
    const integerTicks = d3.range(0, maxValue + 1); // +1 to include the maxValue itself

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
        .style("fill", "#d90429") // add more colors here
        .attr('width', ({ value }) => xScale(value))
        .attr('height', yScale.bandwidth());
}

function toTitleCase(str) {
    return str.toLowerCase().split(' ').map(word => {
        return word.charAt(0).toUpperCase() + word.slice(1);
    }).join(' ');
}

function createDistributionPlotForCategoryData2(atc_code, classes1, class_count1, atc_comparison, classes2, class_count2, elementID1, elementID2, text) {
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
    var margin = { top: 20, right: 150, bottom: 30, left: 40 };
    var width = (plottingBox1.clientWidth - margin.left - margin.right);
    var height = 400 - margin.top - margin.bottom;

    var x0 = d3.scaleBand()
        .rangeRound([0, width], .5)
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
        .attr('width', width )
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
        .attr('transform', function (d, i) { return 'translate(' + (width  - 70) + ',' + i * 20 + ')'; })  // Adjusted x position
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

