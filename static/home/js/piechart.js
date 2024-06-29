

// Define 14 and 7 color scheme 
const color14s = d3.range(14).map(d => d3.interpolateRainbow(d / 14));
const color7s = d3.range(7).map(d => d3.interpolateRainbow(d / 7));
const formatValue = d3.format(",");

// Protein PieChart Function
function createPieChart_Proteins(){
    const pieData = [
        { name: "Adhesion ", value: 14, color: "#9b2226" },
        { name: "Enzyme", value: 854, color: "#ae2012" },
        { name: "Epigenetic regulator", value: 37, color: "#bb3e03"  },
        { name: "GPCR", value: 163, color: "#ee9b00"  },
        { name: "Ion channel", value: 160, color: "#ca6702"  },
        { name: "Kinase", value: 348, color: "#e9d8a6"  },
        { name: "Membrane receptor", value: 67, color: "#94d2bd"  },
        { name: "Nuclear receptor", value: 59, color: "#0a9396"  },
        { name: "Secreted protein ", value: 85, color: "#005f73"  },
        { name: "Structural protein ", value: 25, color: "#001219"  },
        { name: "Surface antigen ", value: 20, color: "#ffd6ff"  },
        { name: "Transcription factor ", value: 7, color: "#e7c6ff"  },
        { name: "Transporter ", value: 172, color: "#c8b6ff"  },
        { name: "Unknown ", value: 967, color: "#3a86ff"  }
      ];
      bakeDonut(pieData);
      
      function bakeDonut(d) {
        let activeSegment;

        // Select the container element
        const container = document.getElementById('chart-container1');
        const size = Math.max(container.clientWidth, container.clientHeight);
        console.log("size "+size);
        const radius = size/2 -20;
        const thickness = 35;

        const data = d.sort((a, b) => b['value'] - a['value']),
                // colorArray = data.map(k => k.color),
                color = d3.scaleOrdinal(color14s);
                // .range(colorArray);
      
        // const max = d3.max(data, (maxData) => maxData.value );
        const chosen = 854;

        const svg = d3.select('#pie-chart-proteins')
        .attr('viewBox', `0 0 ${size} ${size}`)
        .attr('width', size)
        .attr('height', size)
      
        const g = svg.append('g')
        .attr("transform", `translate(${size / 2},${size / 2})`);

        const arc = d3.arc()
        .innerRadius(radius - thickness)
        .outerRadius(radius);
      
        const arcHover = d3.arc()
        .innerRadius(radius - thickness -3)
        .outerRadius(radius + 6);
      
        const pie = d3.pie()
        .value(function(pieData) { return pieData.value; })
        .sort(null);
      
      
        const path = g.selectAll('path')
        .attr('class', 'data-path')
        .data(pie(data))
        .enter()
        .append('g')
        .attr('class', 'data-group')
        .each(function(pathData, i) {
          const group = d3.select(this)
      
          group.append('text')
            .text(`${formatValue(pathData.data.value)}`)
            .attr('class', 'data-text data-text__value')
            .attr('text-anchor', 'middle')
            .attr('dy', '1rem')
      
          group.append('text')
            .text(`${pathData.data.name}`)
            .attr('class', 'data-text data-text__name')
            .attr('text-anchor', 'middle')
            .attr('dy', '3.0rem')
      
          // Set default active segment
          if (pathData.value === chosen) {
            const textVal = d3.select(this).select('.data-text__value')
            .classed('data-text--show', true);
      
            const textName = d3.select(this).select('.data-text__name')
            .classed('data-text--show', true);
          }
      
        })
        .append('path')
        .attr('d', arc)
        .attr('fill', (fillData, i) => color(fillData.data.name))
        .attr('class', 'data-path')
        .on('mouseover', function() {
          const _thisPath = this,
                parentNode = _thisPath.parentNode;
      
          if (_thisPath !== activeSegment) {
      
            activeSegment = _thisPath;
      
            const dataTexts = d3.selectAll('.data-text')
            .classed('data-text--show', false);
      
            const paths = d3.selectAll('.data-path')
            .transition()
            .duration(250)
            .attr('d', arc);
      
            d3.select(_thisPath)
              .transition()
              .duration(250)
              .attr('d', arcHover);
      
            const thisDataValue = d3.select(parentNode).select('.data-text__value')
            .classed('data-text--show', true);
            const thisDataText = d3.select(parentNode).select('.data-text__name')
            .classed('data-text--show', true);
          }
        })
        .each(function(v, i) {
          if (v.value === chosen) {
            const chosenArc = d3.select(this)
            .attr('d', arcHover);
            activeSegment = this;
          }
          this._current = i;
        });
      }
}

// Drug PieChart Function
function createPieChart_Drugs() {
    const data = [
        { name: "Nutraceutical", value: 30 , color: "#18FFFF"},
        { name: "Preclinical", value: 2975 , color: '#0288D1'},
        { name: "Investigational", value: 906 , color: '#BF360C'},
        { name: "Approved", value: 2277 , color: '#F4511E'},
        { name: "Vet-approved", value: 36, color: '#F9A825' },
        { name: "Illicit", value: 35 , color: "#2a9d8f"}
    ];
    bakeDonut(data);
    // "chart-container2"
    // #pie-chart-drugs
    function bakeDonut(d) {
        let activeSegment;

        // Select the container element
        const container = document.getElementById('chart-container2');
        const size = Math.max(container.clientWidth, container.clientHeight);
        console.log("size "+size);
        const radius = size/2 -20;
        const thickness = 35;

        const data = d.sort((a, b) => b['value'] - a['value']),
                colorArray = data.map(k => k.color),
                color = d3.scaleOrdinal()
                .range(colorArray);
      
        const max = d3.max(data, (maxData) => maxData.value );
        // const chosen = 854;

        const svg = d3.select('#pie-chart-drugs')
        .attr('viewBox', `0 0 ${size} ${size}`)
        .attr('width', size)
        .attr('height', size)
      
        const g = svg.append('g')
        .attr("transform", `translate(${size / 2},${size / 2})`);

        const arc = d3.arc()
        .innerRadius(radius - thickness)
        .outerRadius(radius);
      
        const arcHover = d3.arc()
        .innerRadius(radius - thickness -3)
        .outerRadius(radius + 6);
      
        const pie = d3.pie()
        .value(function(data) { return data.value; })
        .sort(null);
      
      
        const path = g.selectAll('path')
        .attr('class', 'data-path')
        .data(pie(data))
        .enter()
        .append('g')
        .attr('class', 'data-group')
        .each(function(pathData, i) {
          const group = d3.select(this)
      
          group.append('text')
            .text(`${formatValue(pathData.data.value)}`)
            .attr('class', 'data-text data-text__value')
            .attr('text-anchor', 'middle')
            .attr('dy', '1rem')
      
          group.append('text')
            .text(`${pathData.data.name}`)
            .attr('class', 'data-text data-text__name')
            .attr('text-anchor', 'middle')
            .attr('dy', '3.0rem')
      
          // Set default active segment
          if (pathData.value === max) {
            const textVal = d3.select(this).select('.data-text__value')
            .classed('data-text--show', true);
      
            const textName = d3.select(this).select('.data-text__name')
            .classed('data-text--show', true);
          }
      
        })
        .append('path')
        .attr('d', arc)
        .attr('fill', (fillData, i) => color(fillData.data.name))
        .attr('class', 'data-path')
        .on('mouseover', function() {
          const _thisPath = this,
                parentNode = _thisPath.parentNode;
      
          if (_thisPath !== activeSegment) {
      
            activeSegment = _thisPath;
      
            const dataTexts = d3.selectAll('.data-text')
            .classed('data-text--show', false);
      
            const paths = d3.selectAll('.data-path')
            .transition()
            .duration(250)
            .attr('d', arc);
      
            d3.select(_thisPath)
              .transition()
              .duration(250)
              .attr('d', arcHover);
      
            const thisDataValue = d3.select(parentNode).select('.data-text__value')
            .classed('data-text--show', true);
            const thisDataText = d3.select(parentNode).select('.data-text__name')
            .classed('data-text--show', true);
          }
        })
        .each(function(v, i) {
          if (v.value === max) {
            const chosenArc = d3.select(this)
            .attr('d', arcHover);
            activeSegment = this;
          }
          this._current = i;
        });
      }
}


function createPieChart_ATClevel1() {
    const data = [
        { name: "Alimentary tract and \nmetabolism", value: 422 },
        { name: "Blood and blood forming\n organs", value: 142 },
        { name: "Cardiovascular system", value: 533 },
        { name: "Dermatologicals", value: 220 },
        { name: "Genito urinary system and\n sex hormones", value: 327 },
        { name: "Systemic hormonal prep, \nexcl sex hormones", value: 65 },
        { name: "General antiinfectives for\n systemic use", value: 380 },
        { name: "Antineoplastic and \nimmunomodulating \nagents", value: 306 },
        { name: "Musculo-skeletal system", value: 167 },
        { name: "Nervous system", value: 445 },
        { name: "Antiparasitic products, \ninsecticides & repellants", value: 65 },
        { name: "Respiratory system", value: 286 },
        { name: "Sensory organs", value: 226 },
        { name: "Various", value: 92 }
    ];
    //"#pie-chart-ATC"
    // #chart-container3
    bakeDonut(data);
    function bakeDonut(d) {
        let activeSegment;

        // Select the container element
        const container = document.getElementById('chart-container3');
        const size = Math.max(container.clientWidth, container.clientHeight);
        console.log("size "+size);
        const radius = size/2 -20;
        const thickness = 35;

        const data = d.sort((a, b) => b['value'] - a['value']),
                // colorArray = data.map(k => k.color),
                color = d3.scaleOrdinal(color14s);
      
        const max = d3.max(data, (maxData) => maxData.value );
        // const chosen = 854;

        const svg = d3.select('#pie-chart-ATC')
        .attr('viewBox', `0 0 ${size} ${size}`)
        .attr('width', size)
        .attr('height', size)
      
        const g = svg.append('g')
        .attr("transform", `translate(${size / 2},${size / 2})`);

        const arc = d3.arc()
        .innerRadius(radius - thickness)
        .outerRadius(radius);
      
        const arcHover = d3.arc()
        .innerRadius(radius - thickness -3)
        .outerRadius(radius + 6);
      
        const pie = d3.pie()
        .value(function(data) { return data.value; })
        .sort(null);
      
      
        const path = g.selectAll('path')
        .attr('class', 'data-path')
        .data(pie(data))
        .enter()
        .append('g')
        .attr('class', 'data-group')
        .each(function(pathData, i) {
          const group = d3.select(this)
          const lines = pathData.data.name.split("\n")
      
          group.append('text')
            .text(`${formatValue(pathData.data.value)}`)
            .attr('class', 'data-text data-text__value')
            .attr('text-anchor', 'middle')
            .attr('dy', '1rem')
      
          const text = group.append('text')
            // .text(`${pathData.data.name}`)
            .attr('class', 'data-text data-text__name')
            .attr('text-anchor', 'middle')
            .attr('dy', '3.0rem')
        
          lines.forEach((line, index) => {
                text.append('tspan')
                    .text(line)
                    .attr('x', 0)
                    .attr('dy', index === 0 ? '3.0rem' : '2rem'); // Adjust line spacing as needed
            });
      
          // Set default active segment
          if (pathData.value === max) {
            const textVal = d3.select(this).select('.data-text__value')
            .classed('data-text--show', true);
      
            const textName = d3.select(this).select('.data-text__name')
            .classed('data-text--show', true);
          }
      
        })
        .append('path')
        .attr('d', arc)
        .attr('fill', (fillData, i) => color(fillData.data.name))
        .attr('class', 'data-path')
        .on('mouseover', function() {
          const _thisPath = this,
                parentNode = _thisPath.parentNode;
      
          if (_thisPath !== activeSegment) {
      
            activeSegment = _thisPath;
      
            const dataTexts = d3.selectAll('.data-text')
            .classed('data-text--show', false);
      
            const paths = d3.selectAll('.data-path')
            .transition()
            .duration(250)
            .attr('d', arc);
      
            d3.select(_thisPath)
              .transition()
              .duration(250)
              .attr('d', arcHover);
      
            const thisDataValue = d3.select(parentNode).select('.data-text__value')
            .classed('data-text--show', true);
            const thisDataText = d3.select(parentNode).select('.data-text__name')
            .classed('data-text--show', true);
          }
        })
        .each(function(v, i) {
          if (v.value === max) {
            const chosenArc = d3.select(this)
            .attr('d', arcHover);
            activeSegment = this;
          }
          this._current = i;
        });
      }
    

    
}

function createPieChart_Mutations() {
    // Main categories data
    const data = [
        { name: "Target", value: 14030 , color: '#BF360C'},
        { name: "Enzyme", value: 5278 , color: '#18FFFF'},
        { name: "Transporter", value: 3205 , color: '#0288D1'},
        { name: "Carrier", value: 822, color: '#F9A825' },
    ];

    // pie-chart-mutations
    bakeDonut(data);
    // "chart-container2"
    // #pie-chart-drugs
    function bakeDonut(d) {
        let activeSegment;

        // Select the container element
        const container = document.getElementById('chart-container4');
        const size = Math.max(container.clientWidth, container.clientHeight);
        console.log("size "+size);
        const radius = size/2 -20;
        const thickness = 35;

        const data = d.sort((a, b) => b['value'] - a['value']),
                colorArray = data.map(k => k.color),
                color = d3.scaleOrdinal()
                .range(colorArray);
      
        const max = d3.max(data, (maxData) => maxData.value );
        // const chosen = 854;

        const svg = d3.select('#pie-chart-mutations')
        .attr('viewBox', `0 0 ${size} ${size}`)
        .attr('width', size)
        .attr('height', size)
      
        const g = svg.append('g')
        .attr("transform", `translate(${size / 2},${size / 2})`);

        const arc = d3.arc()
        .innerRadius(radius - thickness)
        .outerRadius(radius);
      
        const arcHover = d3.arc()
        .innerRadius(radius - thickness -3)
        .outerRadius(radius + 6);
      
        const pie = d3.pie()
        .value(function(data) { return data.value; })
        .sort(null);
      
      
        const path = g.selectAll('path')
        .attr('class', 'data-path')
        .data(pie(data))
        .enter()
        .append('g')
        .attr('class', 'data-group')
        .each(function(pathData, i) {
          const group = d3.select(this)
      
          group.append('text')
            .text(`${formatValue(pathData.data.value)}`)
            .attr('class', 'data-text data-text__value')
            .attr('text-anchor', 'middle')
            .attr('dy', '1rem')
      
          group.append('text')
            .text(`${pathData.data.name}`)
            .attr('class', 'data-text data-text__name')
            .attr('text-anchor', 'middle')
            .attr('dy', '3.0rem')
      
          // Set default active segment
          if (pathData.value === max) {
            const textVal = d3.select(this).select('.data-text__value')
            .classed('data-text--show', true);
      
            const textName = d3.select(this).select('.data-text__name')
            .classed('data-text--show', true);
          }
      
        })
        .append('path')
        .attr('d', arc)
        .attr('fill', (fillData, i) => color(fillData.data.name))
        .attr('class', 'data-path')
        .on('mouseover', function() {
          const _thisPath = this,
                parentNode = _thisPath.parentNode;
      
          if (_thisPath !== activeSegment) {
      
            activeSegment = _thisPath;
      
            const dataTexts = d3.selectAll('.data-text')
            .classed('data-text--show', false);
      
            const paths = d3.selectAll('.data-path')
            .transition()
            .duration(250)
            .attr('d', arc);
      
            d3.select(_thisPath)
              .transition()
              .duration(250)
              .attr('d', arcHover);
      
            const thisDataValue = d3.select(parentNode).select('.data-text__value')
            .classed('data-text--show', true);
            const thisDataText = d3.select(parentNode).select('.data-text__name')
            .classed('data-text--show', true);
          }
        })
        .each(function(v, i) {
          if (v.value === max) {
            const chosenArc = d3.select(this)
            .attr('d', arcHover);
            activeSegment = this;
          }
          this._current = i;
        });
      }

    
}

// Call the createPieChart function to generate the chart
createPieChart_Proteins();
createPieChart_Drugs();
createPieChart_ATClevel1();
createPieChart_Mutations();