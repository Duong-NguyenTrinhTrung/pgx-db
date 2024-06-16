
var color_set =  [
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
var data = [{label: d.label,
          value: d.value,
          color: colors[i], 
          caption: d.caption}]


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
        colors: color_set,
        id: "variant_statistics" // The ID of the element to create the chart in
      }
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
        "text": "Variant summary",
        "fontSize": 32,
        "font": "Arial"
      },
      "subtitle": {
        "text": "For gene "+geneID,
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
      "content": data
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