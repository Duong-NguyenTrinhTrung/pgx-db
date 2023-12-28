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
  "#003049",
  "#ff99c8",
  "#FF4136",
  "#3D9970",
  "#FF851B",
  "#FFDC00",
  "#0074D9",
  "#7FDBFF",
]


// from http://d3pie.org/#generator
function create_and_show_donut(data, colors, elementId, text){
  var pie = new d3pie(elementId, {
    "header": {
      "title": {
        "text": text,
        "fontSize": 24,
        "font": "Arial"
      },
    //   "subtitle": {
    //     "text": "For "+memberStateToFilterBy+", broken down by spending categories",
    //     "color": "#999999",
    //     "fontSize": 18,
    //     "font": "Arial"
    //   },
    //   "titleSubtitlePadding": 25
    },
    "footer": {
      "text": "",
      "color": "#999999",
      "fontSize": 10,
      "font": "Arial",
      "location": "center"
    },
    "size": {
      "canvasWidth": 450,
      "canvasHeight": 405,
      "pieOuterRadius": "80%",
			"pieInnerRadius": "50%"
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