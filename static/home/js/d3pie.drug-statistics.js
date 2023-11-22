var datasetEndpoint = "https://ec.azure-westeurope-prod.socrata.com/resource/hmju-j9mm.json"
var memberStateToFilterBy = "EU28"
var columnToCountBy = "amount"
var columnToLabelBy = "fund"
var color_set1 =  [
  "#00bbf9",
  "#00f5d4",
  "#9b5de5",
  "#f72585",
  "#ffd60a",
  "#eae2b7",
  "#fcbf49",
  "#f77f00",
  "#d62828",
  "#003049"
]

var color_set2 =  [
  "#ff99c8",
  "#FF4136",
  "#3D9970",
  "#FF851B",
  "#FFDC00",
  "#0074D9",
  "#ffd60a",
  "#01FF70",
  "#9b5de5",
  "#7FDBFF",
]
var color_set3 =  [
  "#f2cc8f",
  "#c8b6ff",
  "#3d405b",
  "#ff006e",
  "#2a9d8f",
  "#ffbe0b",
  "#f4f1de",
  "#f72585",
  "#ef476f",
  "#8338ec",
]

var color_set4 =  [
  "#FF4136",
  "#ff99c8",
  "#01FF70",
  "#9b5de5",
  "#7FDBFF",
  "#3D9970",
  "#FF851B",
  "#FFDC00",
  "#0074D9",
  "#ffd60a",
]

var color_set5 =  [
  "#ffd60a",
  "#00bbf9",
  "#00f5d4",
  "#9b5de5",
  "#eae2b7",
  "#fcbf49",
  "#f72585",
  "#f77f00",
  "#d62828",
  "#003049"
]

var color_set6 =  [
  "#f72585",
  "#ef476f",
  "#f2cc8f",
  "#ff006e",
  "#2a9d8f",
  "#ffbe0b",
  "#c8b6ff",
  "#3d405b",
  "#f4f1de",
  "#8338ec",
]



$( document ).ready(function() {
  
  $.getJSON(datasetEndpoint+"?member_state="+memberStateToFilterBy+"&$where=fund%20!=%20%27Total%27", function(result){
    var data = result.map(function (row, n){
      var label = row[columnToLabelBy]
      var value = parseFloat(row[columnToCountBy])
      var caption = row[columnToLabelBy]+" Amount (€): "+ d3.format(",.2f")(value)
      return {label: label, value: value, caption: caption}
    })

    var datasets = [
      {
        colors: color_set1,
        id: "pieChart1" // The ID of the element to create the chart in
      },
      {
        colors: color_set2,
        id: "pieChart2" // The ID of the element to create the chart in
      },
      {
        colors: color_set3,
        id: "pieChart3" // The ID of the element to create the chart in
      },
      {
        colors: color_set4,
        id: "pieChart4" // The ID of the element to create the chart in
      },
      {
        colors: color_set5,
        id: "pieChart5" // The ID of the element to create the chart in
      },
      {
        colors: color_set6,
        id: "pieChart6" // The ID of the element to create the chart in
      },



    ]

    datasets.forEach(function(dataset) {
      create_and_show_donut(data, dataset.colors, dataset.id);
    });

  })
})

// from http://d3pie.org/#generator
function create_and_show_donut(data, colors, elementId){
  var pie = new d3pie(elementId, {
    "header": {
      "title": {
        "text": "Allocations of Cohesion Policy 2014-2020",
        "fontSize": 32,
        "font": "Arial"
      },
      "subtitle": {
        "text": "For "+memberStateToFilterBy+", broken down by spending categories",
        "color": "#999999",
        "fontSize": 18,
        "font": "Arial"
      },
      "titleSubtitlePadding": 25
    },
    "footer": {
      "text": "",
      "color": "#999999",
      "fontSize": 10,
      "font": "Arial",
      "location": "center"
    },
    "size": {
      "canvasWidth": 1100,
      "canvasHeight": 700,
      "pieOuterRadius": "90%",
			"pieInnerRadius": "40%"
    },
		
    "data": {
      "sortOrder": "value-desc",
      "content": data.map(function(d, i) {
        return {
          label: d.label,
          value: d.value,
          color: colors[i], 
          caption: d.caption
        };
      })
    },
    "labels": {
      "outer": {
        "pieDistance": 21
      },
      "inner": {
        "hideWhenLessThanPercentage": 2
      },
      "mainLabel": {
        "fontSize": 17
      },
      "percentage": {
        "color": "#ffffff",
        "fontSize": 18
      },
      "value": {
        "color": "#adadad",
        "fontSize": 18
      },
      "lines": {
        "enabled": true,
        "style": "straight"
      },
      "truncation": {
        "enabled": true
      }
    },
    "tooltips": {
      "enabled": true,
      "type": "placeholder",
      "string": "{label}: {value}, {percentage}%",
      "styles": {
        "fadeInSpeed": 0,
        "backgroundOpacity": 0.71,
        "borderRadius": 10,
        "fontSize": 18
      }
    },
    "effects": {
      "load": {
        "speed": 800
      },
      "pullOutSegmentOnClick": {
        "effect": "linear",
        "speed": 400,
        "size": 14
      }
    },
    "misc": {
      "gradient": {
        "enabled": true,
        "percentage": 65
      }
    }
  });
}