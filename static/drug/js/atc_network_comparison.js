function createDistributionPlot(data, data_all, elementID, text)
{
    $("#result-compare-table").html("");
    // target the .viz container
    const viz = d3.select('#'+elementID)
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

    // linear gradient described for the entire visualization
    // the idea is to have lighter colors toward the top of the svg
    //Defines a linear gradient for the histogram, creating a color transition from top to bottom.
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
    .attr('stop-color', 'white')
    .attr('offset', 0);

    linearGradient
    .append('stop')
    .attr('stop-color', '#d90429')
    .attr('offset', 1);

    //Sets up the group for the histogram, defines the x and y scales, and prepares the data for the histogram.
    const groupHistogram = svgHistogram
    .append('g')
    .attr('transform', `translate(${margin.left}+20  ${margin.top})`);

    // for the horizontal dimension the scale is defined for both the histogram and the density plot
    // ! the function is also used by the histogram function to determine the different bins
    const xScale = d3
    .scaleLinear()
    .domain([d3.min(data_all), d3.max(data_all)])
    .range([0, width]);

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
    .call(yAxisHistogram);

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
    .attr('stroke', '#0c1620')
    .attr('stroke-width', 2);

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
    .tickPadding(10)
    .tickFormat(d3.format('d'))
    .tickValues(d3.ticks(xScale.domain()[0], xScale.domain()[1], Math.ceil(xScale.domain()[1])));

    groupHistogram
    .append('g')
    .attr('class', 'axis x-axis')
    .attr('transform', `translate(0 ${height})`)
    .call(xAxis);
}

function createDistributionPlotForCategoryData(classes, class_count, elementID, text)
{
    $("#result-compare-table").html("");
    const data = [];
    for (var i=0; i<classes.length; i++){
        temp = {
          name: classes[i],
          value: class_count[i],
        }
        console.log("temp  = " + temp.name +" "+temp.value);
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
    
    // target the .viz container
    const viz = d3.select('#'+elementID).html("");

    // in a header include preliminary information about the project
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
    .style("fill", "#d90429") // add more colors here
    .attr('width', ({ value }) => xScale(value))
    .attr('height', yScale.bandwidth());
}

function compareNetworkSize(dataAtcCode, dataAtcComparison, elementID, text)
{
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
    $("#"+elementID).html(htmlData);
}

function measureCentralizationDrugDisease(data, elementID, text)
{
    $("#result-compare-table").html("");
    $("#result-compare-area-text").html("");

    var degreeCentralityDrugData = data["degree_centrality_drug"];
    var betweennessCentralityDrugData = data["betweenness_centrality_drug"];
    var degreeCentralityDiseaseData = data["degree_centrality_disease"];
    var betweennessCentralityDiseaseData = data["betweenness_centrality_disease"];

    var e = $("#"+elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable=`<table><tbody><tr><td colspan="3" style="color: #d90429;font-weight: bold;">Centrality of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<degreeCentralityDrugData.length; i++){
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
    for(var i=0; i<degreeCentralityDiseaseData.length; i++){
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

function measureCentralizationDrugProtein(data, elementID, text)
{
    $("#result-compare-table").html("");
    $("#result-compare-area-text").html("");

    var degreeCentralityDrugData = data["degree_centrality_drug"];
    var betweennessCentralityDrugData = data["betweenness_centrality_drug"];
    var degreeCentralityGeneData = data["degree_centrality_gene"];
    var betweennessCentralityGeneData = data["betweenness_centrality_gene"];

    var e = $("#"+elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable=`<table><tbody><tr><td colspan="3" style="color: #d90429;font-weight: bold;">Centrality of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Degree centrality</td><td>&nbsp;&nbsp;Betweeness centrality</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<degreeCentralityDrugData.length; i++){
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
    for(var i=0; i<degreeCentralityGeneData.length; i++){
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

function detectingCommunityDrugDisease(data, elementID, text)
{
    $("#result-compare-table").html("");
    $("#result-compare-area-text").html("");

    var partitionDrugData = data["partition_drug"];
    var partitionDiseaseData = data["partition_disease"];

    console.log("partitionDrugData: "+partitionDrugData);
    console.log("partitionDiseaseData: "+partitionDiseaseData);

    var e = $("#"+elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable=`<table><tbody><tr><td colspan="2" style="color: #d90429;font-weight: bold;">Community of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<partitionDrugData.length; i++){
        var drugObject = partitionDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var communityValue = drugObject[drugName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="2" style="color: #d90429; font-weight: bold;">Community of disease nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Disease name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<partitionDiseaseData.length; i++){
        var diseaseObject = partitionDiseaseData[i];
        var diseaseName = Object.keys(diseaseObject)[0];
        var communityValue = diseaseObject[diseaseName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${diseaseName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}

function detectingCommunityDrugProtein(data, elementID, text)
{
    $("#result-compare-table").html("");
    $("#result-compare-area-text").html("");

    var partitionDrugData = data["partition_drug"];
    var partitionGeneData = data["partition_gene"];


    var e = $("#"+elementID);
    e.html("");
    e.append(`<h4>${text}</h4><br>`);
    var htmlTable=`<table><tbody><tr><td colspan="2" style="color: #d90429;font-weight: bold;">Community of drug nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Drug name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<partitionDrugData.length; i++){
        var drugObject = partitionDrugData[i];
        var drugName = Object.keys(drugObject)[0];
        var communityValue = drugObject[drugName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${drugName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `<tr></tr><tr><td colspan="2" style="color: #d90429; font-weight: bold;">Community of protein <i>(in genename)</i> nodes</td></tr>
    <tr style="color: #3498db; font-weight: bold;"><td>Gene name</td><td>&nbsp;&nbsp;Community</td></tr>`;
    // Iterate through the data and build table rows
    for(var i=0; i<partitionGeneData.length; i++){
        var geneObject = partitionGeneData[i];
        var geneName = Object.keys(geneObject)[0];
        var communityValue = geneObject[geneName];
        htmlTable += `<tr><td>&nbsp;&nbsp;${geneName.slice(1)}</td><td>&nbsp;&nbsp;${communityValue}</td></tr>`;
    }
    htmlTable += `</tbody></table>`;
    e.append(htmlTable);
}

