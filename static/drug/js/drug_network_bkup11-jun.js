$(function () {
  $("#all-legends").draggable({
    containment: "window",
  });
});
//Pass jsonFiles Here

// var json_GeneralFile = "json/json_GeneralFile.json";
// var json_GeneralFile = "json/json5.json";
// var json_drugData = "json/json_drugData.json";
// var json_proteinData = "json/json_proteinData.json";
// var json_interactionData = "json/json_interactionData.json";

var json_GeneralFile = "/static/json-sample/json_GeneralFile.json";
var json_drugData = "/static/json-sample/json_drugData.json";
var json_proteinData = "/static/json-sample/json_proteinData.json";
var json_interactionData = "/static/json-sample/json_interactionData.json"

if (drug_bank_ids) {
    json_GeneralFile = "/drugs_network/general_data?drug_bank_ids=" + drug_bank_ids.join(',');
    json_drugData = "/drugs_network/drug_data?drug_bank_ids=" + drug_bank_ids.join(',');
    json_proteinData = "/drugs_network/protein_data?drug_bank_ids=" + drug_bank_ids.join(',');
    json_interactionData = "/drugs_network/interaction_data?drug_bank_ids=" + drug_bank_ids.join(',');
}

if (drug_bank_id) {
    json_GeneralFile = "/drug_network/" + drug_bank_id + "/general_data";
    json_drugData = "/drug_network/" + drug_bank_id + "/drug_data";
    json_proteinData = "/drug_network/" + drug_bank_id + "/protein_data";
    json_interactionData = "/drug_network/" + drug_bank_id + "/interaction_data";
}

// code to get the li of the network visualization

document.addEventListener("DOMContentLoaded", function () {
  // Get all <li> elements within the <ul>
  var listItems = document.querySelectorAll(".nav-tabs li");
  console.log("we are here line 44");
  // Loop through the <li> elements
  listItems.forEach(function (li) {
    // Check if the text content of the <a> element within the <li> matches "Network visualization"
    if (li.textContent.trim() === "Network visualization") {
      // Add a click event listener to the <li>
      li.addEventListener("click", function () {
        console.log("Network visualization tab clicked!");
        if (!flag_tabclicked) {
          flag_tabclicked = true;
          if (flag_processData) {
            console.log("chart is created on clicked ");
            createChart(links);
          }
        }
      });
    }
  });
});

$("#loading").show();

let drug_xlsxData;
let protein_xlsxData;
let interaction_xlsxData;
var drugStatusNameForDialog = "";
var selectedDrugName1 = "";

// Function to read the Drugs JSON data file
function readDrugJSON() {
  const jsonFilePath = json_drugData;
  fetch(jsonFilePath)
    .then((response) => response.json())
    .then((jsonData) => {
      // Assuming your JSON data is an array of objects, adjust this code accordingly
      // drug_xlsxData = jsonData.map(item => item.fields);
      if (typeof jsonData === "string") {
        try {
          var drug_xlsxData1 = JSON.parse(jsonData);
          //console.log("Data type is string, Parsing data",drug_xlsxData );
          // var matchingRow = drug_xlsxData.find((row) => row.fields.name === "Sennosides").fields;
          //   console.log("matching row", matchingRow)
          drug_xlsxData = drug_xlsxData1.map((item) => {
            if (item && item.fields && item.pk) {
              item.fields.pk = item.pk;
            }
            return item.fields;
          });
          //console.log("Final Drug Data", drug_xlsxData);
        } catch (error) {
          console.error("Error parsing JSON string:", error);
          return;
        }
      } else {
        drug_xlsxData = jsonData;
      }

      readProteinJSON();
    })
    .catch((error) => {
      console.error("Error reading the JSON file:", error);
    });
}

function readProteinJSON() {
  const jsonFilePath = json_proteinData;

  fetch(jsonFilePath)
    .then((response) => response.json())
    .then((jsonData) => {
      protein_xlsxData = jsonData;
      //console.log("ProteinData", protein_xlsxData);

      readInteractionJSON();
    })
    .catch((error) => {
      console.error("Error reading the file:", error);
    });
}

function readInteractionJSON() {
  const jsonFilePath = json_interactionData;

  fetch(jsonFilePath)
    .then((response) => response.json())
    .then((jsonData) => {
      interaction_xlsxData = jsonData;
      // console.log("InteractionData",interaction_xlsxData);
      // console.log("End of Logs ");
      processData(numberofnodes, slicedata);
    })
    .catch((error) => {
      console.error("Error reading the file:", error);
    });
}

window.onload = function () {
  readDrugJSON();
//   processData(numberofnodes, slicedata);
  // getDrugJsonData(drugBankId);
};

function getDrugJsonData(drugBankId) {
  // Call to Server to get the data
  //
  // protein_xlsxData
  // interaction_xlsxData
  var url = "/get-drug-network";
  $.ajax(
    {
      type: "GET",
      url: url + "?drugbank_id=" + drugBankId,
    },
    function (data) {
      //console.log(data);
    }
  );

  // call process data
  //processData(numberofnodes);
}

var exportButton = document.getElementById("exportButton");
exportButton.addEventListener("click", function () {
  showExportOptions();
});

window.addEventListener("click", function (event) {
  var modal = document.getElementById("exportModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
});

function showExportOptions() {
  // Check if the modal already exists
  var modal = document.getElementById("exportModal");
  if (modal) {
    // If it exists, toggle the modal display and return
    modal.style.display = modal.style.display === "none" ? "block" : "none";
    return;
  }

  // Create the modal container
  modal = document.createElement("div");
  modal.id = "exportModal";
  modal.className = "modal";

  var content = document.createElement("div");
  content.className = "modal-content";
  modal.appendChild(content);

  // ... (rest of the function)

  // Add a close button
  var closeBtn = document.createElement("button");
  closeBtn.innerHTML = "&times;";
  closeBtn.className = "modal-close";
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });
  content.appendChild(closeBtn);

  var title = document.createElement("h2");
  title.textContent = "Export Chart As";
  title.className = "modal-title";
  title.style.marginTop = "20";
  content.appendChild(title);

  // Append the export options to the modal content
  // content.appendChild(createExportOption('View In Full Screen'));
  // content.appendChild(createExportOption('Print Chart'));
  content.appendChild(createExportOption("Download PNG"));
  content.appendChild(createExportOption("Download JPEG"));
  // content.appendChild(createExportOption('Download PDF'));
  // content.appendChild(createExportOption('Download CSV'));
  content.appendChild(createExportOption("Download XLS"));
  // content.appendChild(createExportOption('View Data Table'));

  // Append the modal to the body
  document.body.appendChild(modal);

  // Show the modal
  modal.style.display = "block";
}

function createExportOption(optionText) {
  var optionButton = document.createElement("button");
  optionButton.textContent = optionText;
  optionButton.className = "pgx_btn1"; // add class here
  optionButton.addEventListener("click", function () {
    handleExportOption(optionText);
  });

  // Add CSS for the buttons directly within the function
  var buttonContainer = document.createElement("div");
  buttonContainer.className = "button-container";
  buttonContainer.appendChild(optionButton);

  var style = document.createElement("style");
  style.innerHTML = `
        
        .pgx_btn1 {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background: #fff;
            color: #333;
            font-size: 14px;
            font-weight: 400;
            line-height: 1.42857143;
            text-align: center;
            white-space: nowrap;
            vertical-align: middle;
            touch-action: manipulation;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            display: block;
            margin-bottom: 5px;
            width: 120px;
            cursor:pointer;
        }

        .pgx_btn1:hover {
            color: #333;
            background-color: #d4d4d4;
        }

        .pgx_btn1:focus {
            outline: 5px auto -webkit-focus-ring-color;
        }
        .button-container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    `;
  document.head.appendChild(style);
  return buttonContainer;
}

function handleExportOption(option) {
  switch (option) {
    case "View In Full Screen":
      viewFullScreen();
      break;

    case "Download PNG":
      //console.log("PNG Export Clikced");
      downloadPNG();

      break;
    case "Download JPEG":
      downloadJPEG();
      break;

    case "Download CSV":
      downloadCSV();
      break;
    case "Download XLS":
      downloadXLS();
      break;
    case "View Data Table":
      viewDataTable();
      break;
    default:
      break;
  }
}

function getFilteredSvgContent(svgElement) {
  // Clone the original SVG to avoid altering it
  var clonedSvg = svgElement.cloneNode(true);
  var d3ClonedSvg = d3.select(clonedSvg);

  // Remove hidden links first
  d3ClonedSvg
    .selectAll(".link")
    .filter(function () {
      return (
        this.style.visibility === "hidden" || this.style.display === "none"
      );
    })
    .remove();

  // Remove hidden parent nodes
  d3ClonedSvg
    .selectAll(".node-parent")
    .filter(function () {
      return (
        this.style.visibility === "hidden" || this.style.display === "none"
      );
    })
    .remove();

  // Remove hidden child nodes. This checks if both the circle and text children are hidden.
  d3ClonedSvg
    .selectAll(".node:not(.node-parent)")
    .filter(function () {
      // var circleVisibility = d3.select(this).select('circle').style('visibility');
      // console.log( circleVisibility , 'circleVisibility')
      var textVisibility = d3.select(this).select("text").style("visibility");
      return textVisibility === "hidden";
    })
    .remove();

  return new XMLSerializer().serializeToString(clonedSvg);
}

//Export buttons place
function viewFullScreen() {
  var chartDiv = document.getElementById("chart");
  chartDiv.style.backgroundColor = "white"; // Set background color to white
  chartDiv.requestFullscreen();
}

// Print Chart
function printChart() {
  window.print();
}

// Download PNG
// Download PNG
// Download PNG
function downloadPNG() {
  var svgElement = document.querySelector("#chart svg");

  // Reset transformations by cloning the SVG element and removing any transformations
  var clonedSvgElement = svgElement.cloneNode(true);
  clonedSvgElement.setAttribute("transform", "");

  var svgData = getFilteredSvgContent(clonedSvgElement);
  svgData = addWhiteBackground(svgData);

  // First convert the SVG to canvas
  svgToCanvas(svgData, function (chartCanvas) {
    // Convert the HTML legends to canvas
    html2canvas(document.querySelector("#all-legends")).then(function (
      legendCanvas
    ) {
      // Set the scale factor to double the size of the legend
      var scaleFactor = 2;

      // Create the final canvas with extra width to accommodate the scaled legend
      var finalCanvas = document.createElement("canvas");
      finalCanvas.width = chartCanvas.width + legendCanvas.width * scaleFactor;
      finalCanvas.height = chartCanvas.height;

      var context = finalCanvas.getContext("2d");
      context.fillStyle = "white";
      context.fillRect(0, 0, finalCanvas.width, finalCanvas.height);

      // Draw the chart at its original size without zoom
      context.drawImage(chartCanvas, 0, 0);

      // Draw the scaled-up legend to the right of the chart
      context.drawImage(
        legendCanvas,
        chartCanvas.width,
        (chartCanvas.height - legendCanvas.height * scaleFactor) / 2,
        legendCanvas.width * scaleFactor,
        legendCanvas.height * scaleFactor
      );

      // Now you can save the combined canvas as PNG
      var a = document.createElement("a");
      a.href = finalCanvas.toDataURL("image/png");
      a.download = "chart.png";
      a.click();
    });
  });
}

function svgToCanvas(svgData, callback) {
  var canvas = document.createElement("canvas");
  var context = canvas.getContext("2d");
  var image = new Image();

  // Load all images before rendering SVG onto canvas
  var images = document.querySelector("#chart svg").querySelectorAll("image");
  var loadedCount = 0;

  images.forEach(function (img) {
    var xlinkHref = img.getAttribute("href");
    var imgObj = new Image();
    imgObj.onload = function () {
      loadedCount++;
      if (loadedCount === images.length) {
        renderCanvas();
      }
    };

    if (xlinkHref) {
      //imgObj.src = "http://localhost:8000/" + xlinkHref;
      imgObj.src =
        "https://pharmacogenomics-database-5pltq.ondigitalocean.app" +
        xlinkHref;
    } else {
      loadedCount++;
    }
  });

  function renderCanvas() {
    var scale = 2;
    var width = document.querySelector("#chart svg").clientWidth * scale;
    var height = document.querySelector("#chart svg").clientHeight * scale;

    context.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = width;
    canvas.height = height;
    context.fillStyle = "white";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "black";

    canvg(canvas, svgData, {
      ignoreMouse: true,
      ignoreAnimation: true,
      ignoreDimensions: true,
      scaleWidth: width,
      scaleHeight: height,
      renderCallback: function () {
        callback(canvas);
      },
    });
  }
}

// Download JPEG

function downloadJPEG() {
  var svgElement = document.querySelector("#chart svg");
  var svgData = getFilteredSvgContent(svgElement);
  svgData = addWhiteBackground(svgData);

  // First convert the SVG to canvas
  svgToCanvas(svgData, function (chartCanvas) {
    // Convert the HTML legends to canvas
    html2canvas(document.querySelector("#all-legends")).then(function (
      legendCanvas
    ) {
      // Set the scale factor to double the size of the legend
      var scaleFactor = 2;

      // Create the final canvas with extra width to accommodate the scaled legend
      var finalCanvas = document.createElement("canvas");
      finalCanvas.width = chartCanvas.width + legendCanvas.width * scaleFactor; // add double the legend's width to the chart's width
      finalCanvas.height = chartCanvas.height; // keep the chart's height unchanged

      var context = finalCanvas.getContext("2d");
      context.fillStyle = "white"; // Set background color to white
      context.fillRect(0, 0, finalCanvas.width, finalCanvas.height); // Fill the canvas with white background

      // Draw the chart at its original size
      context.drawImage(chartCanvas, 0, 0);

      // Draw the scaled-up legend to the right of the chart
      context.drawImage(
        legendCanvas,
        chartCanvas.width,
        (chartCanvas.height - legendCanvas.height * scaleFactor) / 2,
        legendCanvas.width * scaleFactor,
        legendCanvas.height * scaleFactor
      );

      // Now you can save the combined canvas as PNG
      var a = document.createElement("a");
      a.href = finalCanvas.toDataURL("image/jpeg", 0.9);
      a.download = "chart.jpeg";
      a.click();
    });
  });
}

function downloadJPEG1() {
  var svgElement = document.querySelector("#chart svg");
  var svgData = getFilteredSvgContent(svgElement);
  svgData = addWhiteBackground(svgData);

  // First convert the SVG to canvas
  svgToCanvas(svgData, function (chartCanvas) {
    // Convert the HTML legends to canvas
    html2canvas(document.querySelector("#all-legends")).then(function (
      legendCanvas
    ) {
      // Double the size of the legend
      var scaleFactor = 2;
      var scaledLegendWidth = legendCanvas.width * scaleFactor;
      var scaledLegendHeight = legendCanvas.height * scaleFactor;

      // Adjust the final canvas size to include the scaled legend
      var finalCanvas = document.createElement("canvas");
      finalCanvas.width = chartCanvas.width + scaledLegendWidth; // sum of the chart width and the double-sized legend width
      finalCanvas.height = Math.max(chartCanvas.height, scaledLegendHeight); // the height should be the max of chart's height or double-sized legend's height

      var context = finalCanvas.getContext("2d");
      context.fillStyle = "white"; // Set background color to white
      context.fillRect(0, 0, finalCanvas.width, finalCanvas.height); // Fill the canvas with white background

      context.drawImage(chartCanvas, 0, 0); // draw the chart as it is

      // Draw the legend on the right side of the chart, doubling its size
      context.drawImage(
        legendCanvas,
        chartCanvas.width,
        0,
        scaledLegendWidth,
        scaledLegendHeight
      );

      // Now you can save the combined canvas as JPEG
      var a = document.createElement("a");
      a.href = finalCanvas.toDataURL("image/jpeg", 0.9); // 0.9 is the quality factor (0 to 1)
      a.download = "chart.jpeg";
      a.click();
    });
  });
}

// Helper function to add a white background rectangle to the SVG
function addWhiteBackground(svgData) {
  var parser = new DOMParser();
  var doc = parser.parseFromString(svgData, "image/svg+xml");
  var svg = doc.documentElement;

  var backgroundRect = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "rect"
  );
  backgroundRect.setAttribute("width", "100%");
  backgroundRect.setAttribute("height", "100%");
  backgroundRect.setAttribute("fill", "white");

  svg.insertBefore(backgroundRect, svg.firstChild);

  return new XMLSerializer().serializeToString(doc);
}

// Download PDF
function downloadPDF() {
  var svgElement = document.querySelector("#chart svg");
  var svgData = new XMLSerializer().serializeToString(svgElement);

  var canvas = document.createElement("canvas");
  var context = canvas.getContext("2d");
  var image = new Image();

  // Load all images before rendering SVG onto canvas
  var images = svgElement.querySelectorAll("image");
  var loadedCount = 0;

  images.forEach(function (img) {
    var xlinkHref = img.getAttribute("href");
    var imgObj = new Image();
    imgObj.onload = function () {
      loadedCount++;
      if (loadedCount === images.length) {
        renderCanvas();
      }
    };

    // Use the href attribute for the image path
    if (xlinkHref) {
      //imgObj.src = "http://localhost:8000/" + xlinkHref;
      imgObj.src =
        "https://pharmacogenomics-database-5pltq.ondigitalocean.app/" +
        xlinkHref;
    } else {
      loadedCount++;
    }
  });

  function renderCanvas() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = svgElement.clientWidth;
    canvas.height = svgElement.clientHeight;
    context.fillStyle = "white"; // Set background color to white
    context.fillRect(0, 0, canvas.width, canvas.height); // Fill with white color

    // Render SVG onto canvas
    canvg(canvas, svgData, {
      ignoreMouse: true,
      ignoreAnimation: true,
      ignoreDimensions: true,
      scaleWidth: canvas.width,
      scaleHeight: canvas.height,
      renderCallback: function () {
        // Convert canvas to image data URL
        var imageData = canvas.toDataURL("image/jpeg");

        // Create a temporary link element to trigger download
        var a = document.createElement("a");
        a.href = imageData;
        a.download = "chart.jpeg";
        a.click();
      },
    });
  }
}

// Download CSV
function downloadCSV() {
  var csvContent = "data:text/csv;charset=utf-8,";
  csvContent += "Source,Target,Type\r\n";

  links.forEach(function (link) {
    var source = link.source.id;
    var target = link.target.id;
    var type = link.type;
    csvContent += source + "," + target + "," + type + "\r\n";
  });

  var encodedURI = encodeURI(csvContent);
  var a = document.createElement("a");
  a.href = encodedURI;
  a.download = "chart.csv";
  a.click();
}

function getFilteredLinksXLSX() {
  var filteredLinks = [];

  // Check the SVG for visible links
  d3.selectAll(".link")
    .filter(function () {
      return (
        this.style.visibility !== "hidden" && this.style.display !== "none"
      );
    })
    .each(function (d) {
      filteredLinks.push(d);
    });

  return filteredLinks;
}

// Download XLS
function downloadXLS() {
  var filteredLinks = getFilteredLinksXLSX();
  //console.log(filteredLinks)
  // Load the XLSX
  var req = new XMLHttpRequest();
  req.open("GET", "/static/d3/data_export_file.xlsx", true);
  req.responseType = "arraybuffer";

  req.onload = function (e) {
    var data = new Uint8Array(req.response);
    var workbook = XLSX.read(data, { type: "array" });

    var firstSheetName = workbook.SheetNames[0];
    var worksheet = workbook.Sheets[firstSheetName];
    var rows = XLSX.utils.sheet_to_json(worksheet);
    // console.log(rows);
    // Filter the rows based on the filtered links
    var filteredRows = rows.filter((row) =>
      filteredLinks.some(
        (link) =>
          link.source.id === row.drug_name &&
          link.source.Drug_type.toLowerCase() === row.drugtype.toLowerCase() &&
          link.target.id === row.protein &&
          link.target.Protein_Class === row.Protein_Class &&
          link.target.DiseaseClass === row.DiseaseClass
      )
    );

    // Create a new worksheet with the filtered rows
    // console.log(filteredRows)
    var newWs = XLSX.utils.json_to_sheet(filteredRows);
    var newWb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(newWb, newWs, firstSheetName);

    // Download the new XLSX file
    XLSX.writeFile(newWb, "filtered_data.xlsx");
  };

  req.send();
}

function downloadXLS11() {
  var workbook = XLSX.utils.book_new();
  var worksheet = XLSX.utils.json_to_sheet(links);
  XLSX.utils.book_append_sheet(workbook, worksheet, "Chart Data");

  var wbout = XLSX.write(workbook, { type: "binary", bookType: "xlsx" });
  function s2ab(s) {
    var buf = new ArrayBuffer(s.length);
    var view = new Uint8Array(buf);
    for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
    return buf;
  }

  var blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
  var url = URL.createObjectURL(blob);

  var a = document.createElement("a");
  a.href = url;
  a.download = "chart.xlsx";
  a.click();
}

// View Data Table
function viewDataTable() {
  var tableData = [];
  tableData.push(["Source", "Target", "Type"]);
  links.forEach(function (link) {
    var source = link.source.id;
    var target = link.target.id;
    var type = link.type;
    tableData.push([source, target, type]);
  });

  var table = document.createElement("table");
  var tableHeader = document.createElement("thead");
  var tableBody = document.createElement("tbody");

  tableData.forEach(function (rowData, rowIndex) {
    var row = document.createElement("tr");
    rowData.forEach(function (cellData, cellIndex) {
      var cellElement =
        rowIndex === 0
          ? document.createElement("th")
          : document.createElement("td");
      cellElement.textContent = cellData;
      row.appendChild(cellElement);
    });
    rowIndex === 0 ? tableHeader.appendChild(row) : tableBody.appendChild(row);
  });

  table.appendChild(tableHeader);
  table.appendChild(tableBody);

  var tableContainer = document.createElement("div");
  tableContainer.appendChild(table);

  var overlay = document.createElement("div");
  overlay.className = "overlay";
  overlay.appendChild(tableContainer);

  document.body.appendChild(overlay);
}

// Drug dialog code place here
function showDialog(title, parentNodeName) {
  var dialog = document.getElementById("dialog");
  var drugName = document.getElementById("drug-name");
  var closeButton = document.getElementById("close-button");
  var oldTabs = document.getElementsByClassName("nav-link");
  var overlay = document.getElementById("overlay");
  selectedDrugName1 = title;

  // Clone tabs and replace old ones to remove previous event listeners
  for (var i = 0; i < oldTabs.length; i++) {
    var newTab = oldTabs[i].cloneNode(true);
    oldTabs[i].parentNode.replaceChild(newTab, oldTabs[i]);
  }

  var tabs = document.getElementsByClassName("nav-link");

  drugName.textContent = parentNodeName;
  dialog.style.display = "block";
  overlay.style.display = "block";

  closeButton.addEventListener("click", function () {
    dialog.style.display = "none";
    overlay.style.display = "none"; // hide the overlay when the dialog is closed
  });

  // Add event listeners to the tabs
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", handleTabClick);
  }

  // Set the first tab as active by default
  tabs[0].classList.add("active");

  // Call the corresponding function for the active tab
  var activeTab = tabs[0].getAttribute("data-tab");
  if (activeTab === "drug-image") {
    showDrugImageTab(selectedDrugName1);
  } else if (activeTab === "drug-description") {
    showDrugDescription(selectedDrugName1);
  } else if (activeTab === "drug-structure") {
    showDrugStructureTab(selectedDrugName1);
  }
  /*
    else if (activeTab === "drug-a") {
      showDrugATab();
    } else if (activeTab === "drug-b") {
      showDrugBTab();
    }
    */

  // Function to handle tab click event
  function handleTabClick(event) {
    // Remove the active class from all tabs
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.remove("active");
    }

    // Add the active class to the clicked tab
    event.target.classList.add("active");
    // showDrugDescription
    // Call the corresponding function based on the tab clicked
    var tabName = event.target.getAttribute("data-tab");
    if (tabName === "drug-image") {
      showDrugImageTab(selectedDrugName1);
    } else if (tabName === "drug-description") {
      showDrugDescription(selectedDrugName1);
    } else if (tabName === "drug-structure") {
      showDrugStructureTab(selectedDrugName1);
    }
    /*
        else if (tabName === "drug-a") {
          showDrugATab();
        } else if (tabName === "drug-b") {
          showDrugBTab();
        }
        */
  }

  // Function to showdrug image
  function showDrugImageTab(drugNameValue) {
    var tabContent = document.querySelector(".tab-content");
    tabContent.innerHTML = ""; // Clear previous content

    // Your code to fetch the row where column name "name" = drugNameValue
    // Assuming you have the data in the global variable 'drug_xlsxData'
    // var matchingRow = drug_xlsxData.find((row) => row.name === drugNameValue);

    const findObjectByName = (array, targetName) => {
      //console.log("Array is ", array);
      return array.find((item) => item.name === targetName);
    };
    //console.log("data Drug Type of", typeof drug_xlsxData);
    //  var matchingRow = drug_xlsxData.find((row) => row.name === drugNameValue);
    const matchingRow = findObjectByName(drug_xlsxData, drugNameValue);
    //console.log("Matching Row Drug ImageTab", matchingRow);

    if (matchingRow) {
      var drugbank_id = matchingRow.pk;

      // Create an img element
      var image = document.createElement("img");

      // Check if the image exists
      image.onerror = function () {
        // If the image does not exist, set the default image path
        image.src = "/static/d3/drug_images/imagenotfound.png";
        // Add the CSS classes to center the image and set the maximum height
        image.classList.add("center-image", "first-tab-image");
        // Append the image to the tabContent
        tabContent.appendChild(image);
      };

      // Set the src attribute to the drug image path
      image.src = "/static/d3/drug_images/" + drugbank_id + ".png";
      // Add the CSS classes to center the image and set the maximum height
      image.classList.add("center-image", "first-tab-image");
      // Append the image to the tabContent
      tabContent.appendChild(image);
    } else {
      // If the drugNameValue is not found in the data, display a default image
      var defaultImage = document.createElement("img");
      defaultImage.src = "/static/d3/drug_images/imagenotfound.png";
      defaultImage.classList.add("center-image", "first-tab-image");
      tabContent.appendChild(defaultImage);
    }
  }

  function showDrugDescription(selectedDrugName1) {
    var tabContent = document.querySelector(".tab-content");
    tabContent.innerHTML = ""; // Clear the existing content

    // Your code to fetch the row where column name "name" matches selectedDrugName1
    // Assuming you have the data in the global variable 'drug_xlsxData'

    // var matchingRow = drug_xlsxData.find((row) => row.name === selectedDrugName1);
    const findObjectByName = (array, targetName) => {
      return array.find((item) => item.name === targetName);
    };
    const matchingRow = findObjectByName(drug_xlsxData, selectedDrugName1);
    //console.log("Matching Row Description", matchingRow);
    if (matchingRow) {
      // Create a table to display the drug information
      var drugInfoTable = document.createElement("div");
      drugInfoTable.classList.add("drug-info-table");
      getDrugStatusName(selectedDrugName1);
      // Create table rows and cells for each field
      var fields = [
        { label: "Drug ID", key: "pk" },
        { label: "Drug Name", key: "name" },
        { label: "Drug Type", key: "drugtype", isConvert: true },
        {
          label: "Drug Approval Status",
          key: "Clinical_status",
          valueForDialog: drugStatusNameForDialog,
        }, // Add Drug_status field with value for dialog
        { label: "Description", key: "description" }, // Move Description to the end
        // Add more fields as needed
      ];

      fields.forEach((field) => {
        var row = document.createElement("div");
        row.classList.add("drug-info-row");

        var labelCell = document.createElement("div");
        labelCell.classList.add("drug-info-cell", "label");
        labelCell.textContent = field.label;
        row.appendChild(labelCell);

        var valueCell = document.createElement("div");
        valueCell.classList.add("drug-info-cell");
        if (field.key === "pk") {
          var drugbankIdValue = matchingRow[field.key];
          var drugbankIdLink =
            "https://go.drugbank.com/drugs/" + drugbankIdValue;

          // Create a new anchor element and set its attributes
          var anchorTag = document.createElement("a");
          anchorTag.href = drugbankIdLink;
          anchorTag.target = "_blank";

          // Set the anchor's innerHTML to include the drug ID and the clickable link
          anchorTag.innerHTML = drugbankIdValue;

          // Set the valueCell's innerHTML to the anchor tag
          valueCell.innerHTML = anchorTag.outerHTML;
        } else if (field.valueForDialog !== undefined) {
          valueCell.textContent = field.valueForDialog;
        } else if (field.isConvert) {
          valueCell.textContent = convertDrugType(matchingRow[field.key]);
        } else {
          valueCell.textContent = matchingRow[field.key];
        }

        row.appendChild(valueCell);
        drugInfoTable.appendChild(row);
      });

      // Append the table to the tabContent
      tabContent.appendChild(drugInfoTable);
    } else {
      // If the selectedDrugName1 is not found in the data, display a default message
      var errorMessage = document.createElement("p");
      errorMessage.textContent =
        "Drug information not found for " + selectedDrugName1;
      tabContent.appendChild(errorMessage);
    }
  }

  function getDrugStatusName(selectedDrugName1) {
    d3.selectAll(".node-parent").filter(function (node) {
      if (node.isParent) {
        if (node.id === selectedDrugName1) {
          //console.log(node.Drug_status)
          drugStatusNameForDialog = node.Drug_status;
          // console.log(drugStatusNameForDialog)
        }
      }
      //console.log(node.Drug_status)
    });
  }
  // Function to convert drugtype reference number into meaningful labels
  function convertDrugType(drugType) {
    if (drugType === 0) {
      return "Biotech";
    } else if (drugType === 1) {
      return "Small Molecule";
    } else {
      return "Unknown";
    }
  }

  function showDrugStructureTab(selectedDrugName1) {
    var tabContent = document.querySelector(".tab-content");
    tabContent.innerHTML = ""; // Clear the existing content

    // Your code to fetch the row where column name "name" matches selectedDrugName1
    // Assuming you have the data in the global variable 'drug_xlsxData

    //var matchingRow = drug_xlsxData.find((row) => row.name === selectedDrugName1);
    const findObjectByName = (array, targetName) => {
      return array.find((item) => item.name === targetName);
    };
    const matchingRow = findObjectByName(drug_xlsxData, selectedDrugName1);
    //console.log("Matching Row Drug Structure", matchingRow);

    if (matchingRow) {
      // Create a table to display the drug structure information
      var drugStructureTable = document.createElement("div");
      drugStructureTable.classList.add("drug-info-table");

      // Fields to add to the table
      var fields = [
        { label: "Indication", key: "indication" },
        { label: "Aliases", key: "aliases", isConvert: true }, // Add isConvert property for "aliases" field
        { label: "Absorption", key: "absorption" },
        { label: "Pharmacodynamics", key: "pharmacodynamics" },
        { label: "Mechanism of Action (MOA)", key: "moa" },
        { label: "Toxicity", key: "toxicity" },
        { label: "Half-life", key: "half_life" },
        { label: "Distribution Volume", key: "distribution_volume" },
        { label: "Protein Binding", key: "protein_binding" },
        { label: "Dosages", key: "dosages" },
        { label: "Properties", key: "properties" },
        // Add more fields as needed
      ];

      fields.forEach((field) => {
        var row = document.createElement("div");
        row.classList.add("drug-info-row");

        var labelCell = document.createElement("div");
        labelCell.classList.add("drug-info-cell", "label");
        labelCell.textContent = field.label;
        row.appendChild(labelCell);

        var valueCell = document.createElement("div");
        valueCell.classList.add("drug-info-cell");
        if (field.isConvert && matchingRow[field.key]) {
          valueCell.appendChild(createAliasList(matchingRow[field.key]));
        } else if (field.key === "dosages") {
          var dosageRegex = /\('([^']*)', '([^']*)'\)/g;
          var matches,
            dosages = [];
          while ((matches = dosageRegex.exec(matchingRow[field.key]))) {
            if (matches[1].trim() && matches[2].trim()) {
              dosages.push(
                `<li><b>${matches[2].replace(";", ",")}</b>: ${matches[1]}</li>`
              ); // Replace semicolon with comma
            }
          }
          valueCell.innerHTML = `<ul>${dosages.join("")}</ul>`;
        } else if (field.key === "properties") {
          var propertiesRegex = /\('([^']*)', '([^']*)'\)/g;
          var matches,
            properties = [];
          while ((matches = propertiesRegex.exec(matchingRow[field.key]))) {
            if (matches[1].trim() && matches[2].trim()) {
              properties.push(`<li><b>${matches[1]}</b>: ${matches[2]}</li>`); // Add <b> tag and replace comma with colon
            }
          }
          valueCell.innerHTML = `<ul>${properties.join("")}</ul>`;
        } else {
          valueCell.textContent = matchingRow[field.key];
        }
        row.appendChild(valueCell);

        drugStructureTable.appendChild(row);
      });

      // Append the table to the tabContent
      tabContent.appendChild(drugStructureTable);
    } else {
      // If the selectedDrugName1 is not found in the data, display a default message
      var errorMessage = document.createElement("p");
      errorMessage.textContent =
        "Drug structure information not found for " + selectedDrugName1;
      tabContent.appendChild(errorMessage);
    }
  }

  // Function to create a bulleted list from the aliases separated by "|"
  function createAliasList11(aliases) {
    var aliasList = document.createElement("ul");
    aliasList.classList.add("alias-list");
    var aliasItems = aliases.split("|");
    aliasItems.forEach((alias) => {
      var listItem = document.createElement("li");
      listItem.classList.add("alias-list-item");
      listItem.textContent = alias;
      aliasList.appendChild(listItem);
    });
    return aliasList;
  }
  // Function to create a string from the aliases separated by "|"
  function createAliasList(aliases) {
    var aliasItems = aliases.split("|").filter((item) => item.trim() !== ""); // Filter out empty strings
    var aliasString = aliasItems.join(", "); // join the items into a string, separated by commas

    var aliasList = document.createElement("p");
    aliasList.textContent = aliasString;

    return aliasList;
  }

  // Function to show drug A
  function showDrugATab() {
    var tabContent = document.querySelector(".tab-content");
    tabContent.textContent = "This is the drug A tab content.";
  }

  // Function to show drug B
  function showDrugBTab() {
    var tabContent = document.querySelector(".tab-content");
    tabContent.textContent = "This is the drug B tab content.";
  }
}

/////Protein Show Dialog

function showDialog_Child(title, childName) {
  var dialog = document.getElementById("dialog1");
  var drugName = document.getElementById("drug-name1");
  var closeButton = document.getElementById("close-button1");
  var oldTabs = document.getElementsByClassName("nav-link1");
  var overlay = document.getElementById("overlay");
  selectedProteinName1 = title;

  // Clone tabs and replace old ones to remove previous event listeners
  for (var i = 0; i < oldTabs.length; i++) {
    var newTab = oldTabs[i].cloneNode(true);
    oldTabs[i].parentNode.replaceChild(newTab, oldTabs[i]);
  }

  var tabs = document.getElementsByClassName("nav-link1");

  drugName.textContent = childName;
  dialog.style.display = "block";
  overlay.style.display = "block";

  closeButton.addEventListener("click", function () {
    dialog.style.display = "none";
    overlay.style.display = "none"; // hide the overlay when the dialog is closed
  });

  // Add event listeners to the tabs
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", handleTabClick);
  }

  // Set the first tab as active by default
  tabs[0].classList.add("active");

  // Call the corresponding function for the active tab
  var activeTab = tabs[0].getAttribute("protein-tab");
  if (activeTab === "protein-image") {
    showProteinImageTab();
  } else if (activeTab === "protein-structure") {
    // console.log("protein:  " + selectedProteinName1)
    showProteinStructureTab(selectedProteinName1);
  }
  showProteinImageTab();
  // Function to handle tab click event
  function handleTabClick(event) {
    // Remove the active class from all tabs
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.remove("active");
    }

    // Add the active class to the clicked tab
    event.target.classList.add("active");

    // Call the corresponding function based on the tab clicked
    var tabName = event.target.getAttribute("data-tab");
    if (tabName === "protein-image") {
      showProteinImageTab();
    } else if (tabName === "protein-structure") {
      // console.log("protein:  " + selectedProteinName1)
      showProteinStructureTab(selectedProteinName1);
    }
  }

  // Function to showdrug image
  // Function to show drug image
  function showProteinImageTab22() {
    var tabContent = document.querySelector(".tab-content1");
    tabContent.innerHTML = ""; // Clear previous content

    // Create an img element
    var image = document.createElement("img");
    image.src = "/static/d3/drug_images/imagenotfound.png";
    image.classList.add("center-image", "first-tab-image"); // Add CSS classes

    // Append the image to the tabContent
    tabContent.appendChild(image);
  }

  function showProteinImageTab() {
    drugNameValue = selectedProteinName1;
    var tabContent = document.querySelector(".tab-content1");
    tabContent.innerHTML = ""; // Clear previous content

    // Your code to fetch the row where column name "name" = drugNameValue
    // Assuming you have the data in the global variable 'drug_xlsxData'
    var matchingRow = protein_xlsxData.find(
      (row) => row.uniprot_ID === drugNameValue
    );
    // console.log(matchingRow)
    if (matchingRow) {
      var drugbank_id = matchingRow.uniprot_ID;

      // Create an img element
      var image = document.createElement("img");

      // Check if the image exists
      image.onerror = function () {
        // If the image does not exist, set the default image path
        image.src = "/static/d3/protein_images/imagenotfound.png";
        // Add the CSS classes to center the image and set the maximum height
        image.classList.add("center-image", "first-tab-image");
        // Append the image to the tabContent
        tabContent.appendChild(image);
      };

      // Set the src attribute to the drug image path
      image.src = "/static/d3/protein_images/" + drugbank_id + ".png";
      // Add the CSS classes to center the image and set the maximum height
      image.classList.add("center-image", "first-tab-image");
      // Append the image to the tabContent
      tabContent.appendChild(image);
    } else {
      // If the drugNameValue is not found in the data, display a default image
      var defaultImage = document.createElement("img");
      defaultImage.src = "/static/d3/protein_images/imagenotfound.png";
      defaultImage.classList.add("center-image", "first-tab-image");
      tabContent.appendChild(defaultImage);
    }
  }

  function showProteinStructureTab(proteinName11111) {
    //console.log("dd: " + proteinName11111);
    var tabContent = document.querySelector(".tab-content1");
    tabContent.innerHTML = ""; // Clear the existing content

    // Your code to fetch the row where column name "name" matches selectedDrugName1
    // Assuming you have the data in the global variable 'protein_xlsxData'
    var matchingRow = protein_xlsxData.find(
      (row) => row.uniprot_ID === proteinName11111
    );
    // console.log(matchingRow);
    if (matchingRow) {
      // Create a table to display the protein structure information
      var proteinStructureTable = document.createElement("div");
      proteinStructureTable.classList.add("protein-info-table");

      // Fields to add to the table
      var fields = [
        { label: "Uniprot ID", key: "uniprot_ID" },
        { label: "Gene Name", key: "genename" },
        { label: "Gene ID", key: "geneID" },
        { label: "Entry Name", key: "entry_name" },
        { label: "Protein Name", key: "protein_name" },
        { label: "Protein Class", key: "Protein_class" },
        // Add more fields as needed
      ];

      fields.forEach((field) => {
        var row = document.createElement("div");
        row.classList.add("protein-info-row");

        var labelCell = document.createElement("div");
        labelCell.classList.add("protein-info-cell", "label");
        labelCell.textContent = field.label;
        row.appendChild(labelCell);

        var valueCell = document.createElement("div");
        valueCell.classList.add("protein-info-cell");

        // Modify the "Uniprot ID" field to include the link
        if (field.key === "uniprot_ID" || field.key === "geneID") {
          var hyperlink = document.createElement("a");
          var matchingValue = matchingRow[field.key];

          if (field.key === "uniprot_ID") {
            hyperlink.href = "https://www.uniprot.org/uniprot/" + matchingValue;
          } else {
            hyperlink.href =
              "https://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=" +
              matchingValue;
          }

          hyperlink.target = "_blank"; // Open link in new tab
          hyperlink.textContent = "";

          // Create a new anchor element for the matching value
          var valueAnchor = document.createElement("a");
          valueAnchor.href = hyperlink.href;
          valueAnchor.target = hyperlink.target;
          valueAnchor.textContent = matchingValue;

          // Clear the existing content of valueCell and append both anchor tags
          valueCell.innerHTML = "";
          valueCell.appendChild(valueAnchor);
          valueCell.appendChild(document.createTextNode(" "));
          valueCell.appendChild(hyperlink);
        } else {
          valueCell.textContent = matchingRow[field.key];
        }

        row.appendChild(valueCell);
        proteinStructureTable.appendChild(row);
      });

      // Append the table to the tabContent
      tabContent.appendChild(proteinStructureTable);
    } else {
      // If the selectedDrugName1 is not found in the data, display a default message
      var errorMessage = document.createElement("p");
      errorMessage.textContent =
        "Protein structure information not found for " + proteinName11111;
      tabContent.appendChild(errorMessage);
    }
  }
}

//Interaction Dialog
function showDialog_Links(title, interactionTy) {
  //console.log("title: " + title)
  var dialog = document.getElementById("dialog2");
  var drugName = document.getElementById("drug-name2");
  var closeButton = document.getElementById("close-button2");
  var oldTabs = document.getElementsByClassName("nav-link2");
  var overlay = document.getElementById("overlay");
  selectedInteractionName1 = title;

  // Clone tabs and replace old ones to remove previous event listeners
  for (var i = 0; i < oldTabs.length; i++) {
    var newTab = oldTabs[i].cloneNode(true);
    oldTabs[i].parentNode.replaceChild(newTab, oldTabs[i]);
  }

  var tabs = document.getElementsByClassName("nav-link2");

  drugName.textContent = title;
  dialog.style.display = "block";
  overlay.style.display = "block"; // show the overlay when the dialog is shown

  closeButton.addEventListener("click", function () {
    dialog.style.display = "none";
    overlay.style.display = "none"; // hide the overlay when the dialog is closed
  });

  // Add event listeners to the tabs
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", handleTabClick);
  }

  // Set the first tab as active by default
  tabs[0].classList.add("active");

  // Call the corresponding function for the active tab
  var activeTab = tabs[0].getAttribute("data-tab");
  if (activeTab === "interaction-strcuture") {
    showInteractionTab(selectedInteractionName1);
  }

  // Function to handle tab click event
  function handleTabClick(event) {
    // Remove the active class from all tabs
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.remove("active");
    }

    // Add the active class to the clicked tab
    event.target.classList.add("active");

    // Call the corresponding function based on the tab clicked
    var tabName = event.target.getAttribute("data-tab");
    if (tabName === "interaction-strcuture") {
      showInteractionTab(selectedInteractionName1);
    }
  }

  // Function to showdrug image
  // Function to show drug image
  function showInteractionTab1(selectedInteractionName1) {
    var tabContent = document.querySelector(".tab-content2");
    tabContent.innerHTML = ""; // Clear previous content

    // Append the image to the tabContent
    //tabContent.appendChild(image);
  }

  function showInteractionTab(selectedInteractionName1) {
    var tabContent = document.querySelector(".tab-content2");
    tabContent.innerHTML = ""; // Clear previous content

    // Your code to fetch the row where columns "drug_bankID", "uniprot_ID", and "interaction_type" matches interaction_source, interaction_target, and selectedInteractionName1 respectively
    // Assuming you have the data in the global variable 'interaction_xlsxData'
    var matchingRow = interaction_xlsxData.find(
      (row) =>
        row.drugbank_id === interaction_source &&
        row.uniprot_ID_id === interaction_target &&
        row.interaction_type.toLowerCase() ===
          selectedInteractionName1.toLowerCase()
    );

    if (matchingRow) {
      // Create a table to display the interaction information
      var interactionInfoTable = document.createElement("div");
      interactionInfoTable.classList.add("interaction-info-table");

      // Create table rows and cells for each field
      var fields = [
        { label: "Interaction Type", key: "interaction_type" },
        { label: "Known Action", key: "known_action" },
        { label: "Actions", key: "actions" },
        { label: "PubMed IDs", key: "pubmed_ids" },
        // Add more fields as needed
      ];

      fields.forEach((field) => {
        var row = document.createElement("div");
        row.classList.add("interaction-info-row");

        var labelCell = document.createElement("div");
        labelCell.classList.add("interaction-info-cell", "label");
        labelCell.textContent = field.label;
        row.appendChild(labelCell);

        var valueCell = document.createElement("div");
        valueCell.classList.add("interaction-info-cell");

        // Check if the current field key is 'pubmed_ids'
        if (field.key === "pubmed_ids") {
          // Create a new <div> element to hold the list of IDs
          var divElement = document.createElement("div");

          // Split the IDs string on "|"
          var ids = matchingRow[field.key].split("|");

          // Create a new <span> element for each ID
          ids.forEach((id, index) => {
            // Create a hyperlink for each ID
            var link = document.createElement("a");
            link.href = "https://pubmed.ncbi.nlm.nih.gov/" + id;
            link.target = "_blank"; // Open link in a new tab
            link.textContent = id;

            // Append the link to the div
            divElement.appendChild(link);

            // Add a comma and a space after each ID, except the last one
            if (index !== ids.length - 1) {
              divElement.append(" , ");
            }
          });

          // Append the div to the value cell
          valueCell.appendChild(divElement);
        } else {
          valueCell.textContent = matchingRow[field.key];
        }

        row.appendChild(valueCell);
        interactionInfoTable.appendChild(row);
      });

      // Append the table to the tabContent
      tabContent.appendChild(interactionInfoTable);
    } else {
      // If the selectedInteractionName1 is not found in the data, display a default message
      var errorMessage = document.createElement("p");
      errorMessage.textContent =
        "Interaction information not found for " + selectedInteractionName1;
      tabContent.appendChild(errorMessage);
    }
  }
}

var width = 400;
var height = 300;
var nodes = []; // Declare nodes array outside of the createChart function
var links = []; // Declare links array outside of the createChart function
var thresholdSlider = document.getElementById("threshold-slider");
var thresholdValueLabel = document.getElementById("threshold-value");
var chartDataJ;
var selectedDrugName1 = "";
var selectedProteinName1 = "";
var selectedInteractionName1 = "";
var hiddenDrugStatuses = {};
var hiddenProteinClasses = {};
var hiddenDiseaseClasses = {};
var hiddenDrugTypes = {};
var hiddenInteractionTypes = {};
var nodeImages = {};
let drugStatusIndices = {};
let drugTypeIndices = {};
var currentFilters;
var interaction_source = "";
var interaction_target = "";
let thredhold_value = 0;
let child_nodes = 0;
// var imagePaths11 = {
//     Nutraceutical: "/static/d3/images/capsules/left0.png",
//     Experimental: "/static/d3/images/capsules/left1.png",
//     Investigational: "/static/d3/images/capsules/left2.png",
//     Approved: "/static/d3/images/capsules/left3.png",
//     'Vet-approved': "/static/d3/images/capsules/left4.png",
//     Illicit: "/static/d3/images/capsules/left5.png"
// };

var imagePaths11 = {
  Nutraceutical: "images/left0.png",
  Experimental: "images/left1.png",
  Investigational: "images/left2.png",
  Approved: "images/left3.png",
  "Vet-approved": "images/left4.png",
  Illicit: "images/left5.png",
};

var colorOptions = [
  "#e71f73",
  "#d5a100",
  "#0a5517",
  "#061755",
  "#941a4c",
  "#3d3d3d",
];

var colorCodes = {
  Nutraceutical: "#e71f73",
  Experimental: "#d5a100",
  Investigational: "#0a5517",
  Approved: "#061755",
  "Vet-approved": "#941a4c",
  Illicit: "#3d3d3d",
};

var colorCodesDrugType = {
  Biotech: "#03A9F4",
  "Small Molecule": "#ff5722",
};
var colorCodesDrugType_images = {
  "#03A9F4": "/static/d3/images/capsules/right0.png",
  "#ff5722": "/static/d3/images/capsules/right1.png",
};
var colorCodesDrugType = {
  Biotech: "#03A9F4",
  "Small Molecule": "#ff5722",
};
var colorPaletteDrugType = {
  "#03A9F4": "#03A9F4", // Biotech
  "#ff5722": "#ff5722", // Small molecule
};

var colorPalette = {
  "#e71f73": "/static/d3/images/capsules/left0.png",
  "#d5a100": "/static/d3/images/capsules/left1.png",
  "#0a5517": "/static/d3/images/capsules/left2.png",
  "#3d3d3d": "/static/d3/images/capsules/left3.png",
  "#941a4c": "/static/d3/images/capsules/left4.png",
  "#061755": "/static/d3/images/capsules/left5.png",
};

var colorImageMap = {
  "#e71f73": "/static/d3/images/capsules/left0.png",
  "#d5a100": "/static/d3/images/capsules/left1.png",
  "#0a5517": "/static/d3/images/capsules/left2.png",
  "#061755": "/static/d3/images/capsules/left3.png",
  "#941a4c": "/static/d3/images/capsules/left4.png",
  "#3d3d3d": "/static/d3/images/capsules/left5.png",
};
var clinicalStatusMap = {
  0: "Nutraceutical",
  1: "Experimental",
  2: "Investigational",
  3: "Approved",
  4: "Vet-approved",
  5: "Illicit",
};
////Drugs Images Setting Variables
//0 -> Nutraceutical, 1 - Experimental, 2- Investigational, 3- Approved , 4 - Vet approved, 5 - Illicit

var drugStatuses = [
  "Nutraceutical",
  "Experimental",
  "Investigational",
  "Approved",
  "Vet-approved",
  "Illicit",
];
var drugTypes = ["Biotech", "Small Molecule"];

// Generate all combinations of leftXrightY.png for the image paths
var imagePaths = {};
Object.keys(colorCodes).forEach((key, i) => {
  Object.keys(colorCodesDrugType).forEach((key2, j) => {
    var keyCombo = key + "|" + key2;
    imagePaths[keyCombo] = `/static/d3/images/capsules/left${i}right${j}.png`;
  });
});

// Function to convert xlsx to JSON
function xlsxToJson(file, callback) {
  fetch(file)
    .then((response) => response.blob())
    .then((blob) => {
      var reader = new FileReader();
      reader.onload = function (e) {
        var data = new Uint8Array(e.target.result);
        var workbook = XLSX.read(data, { type: "array" });
        var jsonData = XLSX.utils.sheet_to_json(
          workbook.Sheets[workbook.SheetNames[0]]
        );

        callback(jsonData);
      };
      reader.readAsArrayBuffer(blob);
    })
    .catch((error) => {
      console.error("Error reading the file:", error);
    });
}

let flag_tabclicked = false;
let flag_processData = false;

let numberofnodes = 1;
let slicedata = 200;

console.log(slicedata, "slicedata");

window.parent.postMessage({ data: slicedata }, "*");

function processData(numberofnodes, slicedata) {
  const jsonFilePath = json_GeneralFile; // JSON file path

  //console.log("Inside Process Data Function11");
  fetch(jsonFilePath)
    .then((response) => response.json())
    .then((data) => {
      console.log(data, "here is the data ");

      const uniqueProteinClasses = [
        ...new Set(data.map((d) => d.protein_name)),
      ];

      // Extract nodes and links from the JSON data
      // console.log("inside processData: ", data);
      chartDataJ = data;

      let filteredData = data.filter(
        (row) => row.Phase !== "1" && row.Phase !== "2"
      );

      if (thredhold_value < 5 && child_nodes > 180) {
        filteredData = filteredData.slice(0, slicedata);
      }

      console.log(filteredData, "filternodes");

      filteredData.forEach(function (row) {
        var drugName = row.drug_name;
        var drugID = row.drugbank_id;
        var protein = row.protein;
        var genename = row.gene_name;
        var interaction =
          row.interaction_type.charAt(0).toUpperCase() +
          row.interaction_type.slice(1);
        // var interaction = row.interaction

        var disease_interaction;
        var disease_phase;
        disease_interaction = "Phase" + row.Phase;
        disease_phase = row.Phase;

        var drugStatus = clinicalStatusMap[row.Drug_status];
        var drugType = row.drugtype;
        var proteinClass = row.Protein_Class;

        var disease = row.Disease_name; // getting the new disease
        var Disease_class = row.Disease_class;

        if (
          !nodes.find(function (node) {
            return node.id === drugName;
          })
        ) {
          nodes.push({
            id: drugName,
            isParent: true,
            radius: 10,
            Drug_status: drugStatus,
            Drug_type: drugType,
            Drug_ID: drugID,
          }); // Include the "Drug_status" value in the node object
        }

        if (
          !nodes.find(function (node) {
            return node.id === protein;
          })
        ) {
          nodes.push({
            id: protein,
            isParent: false,
            radius: 5,
            genename: genename,
            Protein_Class: proteinClass,
            child_type: "protein_type",
          }); // Include the "Protein_Class" value in the node object
        }
        // tag1
        if (
          !nodes.find(function (node) {
            return node.id === disease;
          })
        ) {
          nodes.push({
            id: disease,
            isParent: false,
            child_type: "disease_type",
            radius: 5,
            DiseaseClass: Disease_class,
            disease_phase: disease_phase,
            // Protein_Class: proteinClass,
          }); // Include the "Protein_Class" value in the node object
        }

        if (
          !nodes.find(function (node) {
            return node.id === drugName;
          })
        ) {
          nodes.push({ id: drugName, isParent: true, radius: 10 });
        }

        if (
          !nodes.find(function (node) {
            return node.id === protein;
          })
        ) {
          nodes.push({ id: protein, isParent: false, radius: 5 });
        }

        links.push({
          source: drugName,
          target: protein,
          type: interaction,
          // disease_type: "temp"
        });

        links.push({
          source: drugName,
          target: disease,
          type: disease_interaction,
          // disease_type: disease_interaction // You can customize the type for disease links
        });

        //console.log(links, "here are the type")
      });
      //console.log("here are the links", links);
      var childNodeMap = {};
      links.forEach(function (link) {
        if (!link.target.isParent) {
          var childNodeId = link.target.id;
          childNodeMap[childNodeId] = (childNodeMap[childNodeId] || 0) + 1;
        }
      });

      // Assign the parent count to each child node
      nodes
        .filter(function (d) {
          return !d.isParent;
        })
        .forEach(function (node) {
          node.degree = childNodeMap[node.id] || 0;
        });

      // Set the maximum value of the threshold slider
      thredhold_value = nodes.filter(function (node) {
        return node.isParent;
      }).length;

      child_nodes = nodes.filter(function (node) {
        return !node.isParent;
      }).length;

      thresholdSlider.max = numberofnodes;
      console.log(numberofnodes, "here are the number of nodes");
      if (thredhold_value <= numberofnodes || slicedata > filteredData.length) {
        thresholdSlider.max = thredhold_value;
        document.getElementById("GetmoreData").disabled = true;
        document.getElementById("GetmoreData").innerHTML =
          "Maximum data reached";
      }

      if (slicedata > filteredData.length) {
        thresholdSlider.value = 50;
        thresholdValueLabel.textContent = thredhold_value;
      } else {
        thresholdSlider.value = 50;
        thresholdValueLabel.textContent = numberofnodes;
      }

      // Set the default value of the threshold slider to the maximum

      // tag5
      // Create the chart using D3.js

      createChart(links);

      // Add an event listener to detect changes in the threshold slider value
      thresholdSlider.addEventListener("input", function () {
        thresholdValueLabel.textContent = thresholdSlider.value;
        updateChartVisibility();
      });
    })
    .catch((error) => {
      console.error("Error reading the JSON file:", error);
    });

  // d3.select("#loading").style("height", "800px");
}

// Read the data from the Excel file

var link;
var node;
var svg, chart;
var simulation = null;

// Create the Forced Directed Network Chart
function createChart(links) {
  d3.select("#chart").selectAll("*").remove();
  //console.log("Latest Edit CreateCHart_13_jan_2024_A");
  var container = d3.select("#chart");
  //debugger
  var svgWidth = [container.node().getBoundingClientRect().width] - 100;
  var svgHeight = [container.node().getBoundingClientRect().height] - 100;
  //var containerWidth = 500;
  //var containerHeight = 500;
  //console.log("Width : "+containerWidth+"  ----  Height : "+containerHeight);

  var zoom = d3
    .zoom()
    .scaleExtent([0.1, 10])
    .on("zoom", function (event, d) {
      //console.log("zoom event:", event);
      //console.log("event.transform:", event.transform);
      svg.attr("transform", event.transform.toString());
    });

  // SVG creation with zoom behavior
  svg = container
    .append("svg")
    .attr("width", svgWidth)
    .attr("height", svgHeight)
    // .style("background-color" , "red")
    .call(zoom)
    .append("g"); // Append group element to SVG

  chart = svg
    .append("g") // Assign the group element to the 'chart' variable
    .attr("class", "chart");

  var chargeStrength = parseFloat(
    getComputedStyle(document.documentElement).getPropertyValue(
      "--charge-strength"
    )
  );
  var distanceBetweenNodes = 60;
  var noOfTotalNodes11 = links.length;
  console.log(links.length, "link length");

  if (noOfTotalNodes11 < 100) {
    chargeStrength = -250;

    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 99 && noOfTotalNodes11 < 200) {
    chargeStrength = -250;
    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 199 && noOfTotalNodes11 < 250) {
    chargeStrength = -250;
    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 249 && noOfTotalNodes11 < 300) {
    chargeStrength = -250;
    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 299 && noOfTotalNodes11 < 350) {
    chargeStrength = -250;
    var distanceBetweenNodes = 200;
    // change2
  } else if (noOfTotalNodes11 > 349 && noOfTotalNodes11 < 400) {
    console.log("check6");
    chargeStrength = -100;
    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 399 && noOfTotalNodes11 < 999) {
    console.log("check8", noOfTotalNodes11);
    chargeStrength = -250;
    var distanceBetweenNodes = 200;
  } else if (noOfTotalNodes11 > 1000 && noOfTotalNodes11 < 2999) {
    console.log("check9", noOfTotalNodes11);
    chargeStrength = -250;
    var distanceBetweenNodes = 100;
  } else if (noOfTotalNodes11 > 3000) {
    console.log("check10", noOfTotalNodes11);
    chargeStrength = -250;
    var distanceBetweenNodes = 60;
  }

  simulation = d3
    .forceSimulation(nodes)
    .force(
      "link",
      d3
        .forceLink(links)
        .id(function (d) {
          return d.id;
        })
        .distance(distanceBetweenNodes)
    )
    .force("charge", d3.forceManyBody().strength(chargeStrength))
    // Adding centering forces for X and Y coordinates
    .force("x", d3.forceX(svgWidth / 2).strength(0.1))
    .force("y", d3.forceY(svgHeight / 2).strength(0.1))

    .on("end", function () {
      nodes.forEach(function (node) {
        node.fx = node.x;
        node.fy = node.y;
      });
    });

  link = svg
    .selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("class", "link")
    .style("stroke", function (d) {
      return colorMap[d.type.toLowerCase()];
    })
    .style("stroke-dasharray", function (d) {
      if (d.target.child_type === "disease_type") {
        return "2,2";
      }
    })
    .style("stroke-width", 2)
    .on("click", function (event, d) {
      interaction_source = d.source.Drug_ID;
      interaction_target = d.target.id;

      showDialog_Links(d.type, d.type);
      //showDialog_Interaction(d.id, d.id);
    });

  node = svg
    .selectAll(".node")
    .data(nodes)
    .enter()
    .append("g")
    .attr("class", "node")
    .call(drag(simulation));

  var childNodeMap = {};
  links.forEach(function (link) {
    if (!link.target.isParent) {
      var childNodeId = link.target.id;
      childNodeMap[childNodeId] = (childNodeMap[childNodeId] || 0) + 1;
    }
  });

  // Add the following code to calculate the size of the child nodes based on the number of connected parent nodes
  var childNodeMap = {};
  links.forEach(function (link) {
    if (!link.target.isParent) {
      var childNodeId = link.target.id;
      childNodeMap[childNodeId] = (childNodeMap[childNodeId] || 0) + 1;
    }
  });

  // Add the following code to calculate the size of the child nodes based on the number of connected parent nodes
  //  tag2
  node
    .filter(function (d) {
      return d.child_type === "protein_type" && !d.isParent;
    })
    .append("circle")
    .attr("r", function (d) {
      var uniqueSources = new Set();
      link.filter(function (templink) {
        if (templink.target.id === d.id) {
          uniqueSources.add(templink.source.id);
        }
      });
      var child_size = Array.from(uniqueSources).length;
      if (child_size > 25) {
        return 30;
      } else {
        return 5 + child_size;
      }
    })
    .style("fill", function (d) {
      return proteinColorMap[d.Protein_Class] || "steelblue";
    })
    .on("click", function (event, d) {
      showDialog_Child(d.id, d.id);
    });

  node
    .filter(function (d) {
      // change1
      return (
        d.child_type === "disease_type" &&
        !d.isParent &&
        d.disease_phase !== 1 &&
        d.DiseaseClass
      );
    })
    .append("path")
    .attr("d", "M 0 0 L 8 16 L -8 16 Z") // Path data for a triangle
    .style("fill", function (d) {
      return DiseaseColorMap[d.DiseaseClass] || "black";
    });

  node
    .on("click", function (event, d) {
      window.open(`https://clinicaltrials.gov/search?cond=${d.id}`, "_blank");
    })
    // Attach cursor style change on mouseover to all nodes
    .on("mouseover", function () {
      d3.select(this).style("cursor", "pointer");
    });

  node
    .filter((d) => d.child_type === "disease_type")
    .on("mouseover", function (event, d) {
      d3.select(this).style("cursor", "pointer");
      tooltip2.transition().style("opacity", 0.9);
      tooltip2
        .html(d.id)
        .style("left", event.pageX + "px")
        .style("top", event.pageY + "px");
    })
    .on("mouseout", function () {
      tooltip2.transition().style("opacity", 0);
    });

  // Attach click event to all nodes

  // Define a tooltip div with class "tooltip2"
  var tooltip2 = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip2")
    .style("opacity", 0);

  node
    .filter(function (d) {
      return d.isParent;
    })
    .attr("class", "node-parent")
    .append("image")
    .attr("class", "node-image")
    .attr("xlink:href", function (d) {
      var key = d.Drug_status + "|" + d.Drug_type;
      //return imagePaths[key];

      return imagePaths[key];
    })
    .attr("x", -12)
    .attr("y", -12)
    .attr("width", 30)
    .attr("height", 30)
    .on("click", function (event, d) {
      showDialog(d.id, d.id);
    });

  node
    .filter(function (d) {
      return d.isParent;
    })
    .append("text")
    .attr("dx", 14)
    .attr("dy", "2em")
    .text(function (d) {
      return d.id;
    })
    .attr("class", "node-label");

  // node.append("title").text(function (d) {
  //     return d.id;
  // });

  node
    .filter(function (d) {
      //return !d.isParent;
      return !d.isParent && d.disease_phase !== 1;
    })
    .append("text")
    .attr("dx", 10)
    .attr("dy", ".25em")
    .text(function (d) {
      return d.genename;
    })
    .attr("class", "node-label");
  // tag4

  simulation.on("tick", function () {
    link
      .attr("x1", function (d) {
        return Math.max(0, Math.min(svgWidth, d.source.x));
      })
      .attr("y1", function (d) {
        return Math.max(0, Math.min(svgHeight, d.source.y));
      })
      .attr("x2", function (d) {
        return Math.max(0, Math.min(svgWidth, d.target.x));
      })
      .attr("y2", function (d) {
        if (d.target.child_type === "disease_type") {
          return Math.max(0, Math.min(svgHeight, d.target.y)) + 8;
        } else {
          return Math.max(0, Math.min(svgHeight, d.target.y));
        }
      });

    node.attr("transform", function (d) {
      return `translate(${Math.max(
        0,
        Math.min(svgWidth, d.x)
      )},${Math.max(0, Math.min(svgHeight, d.y))})`;
    });
  });

  // Enable drag behavior for nodes
  function drag(simulation) {
    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      // Removed setting of d.fx and d.fy to null here
    }

    return d3
      .drag()
      .on("start", dragStarted)
      .on("drag", dragged)
      .on("end", dragEnded);
  }

  // Button click handlers
  d3.select(".zoom-in-btn").on("click", function () {
    zoom.scaleBy(svg.transition().duration(750), 1.1); // scale up by 10%
  });

  d3.select(".zoom-out-btn").on("click", function () {
    //console.log("Zoom out called");
    zoom.scaleBy(svg.transition().duration(750), 0.9); // scale down by 10%
  });

  //console.log("Chart created.");
  // Finish updating chart
  $("#loading").hide();
  //$("#loading").hide();
  updateChartVisibility();
  createLegend();

  // here is the logic to add the height  of the  iframe there

  $(function () {
    // Get the height of the #all-legends element
    var height = $("#all-legends").height() + 180;
    console.log(height, svgHeight, "Height of #all-legends: " + height + "px");

    localStorage.setItem("jsonData", height);
  });

  createLegend_status();
  createLegend_drugType();
  createProteinsLegend();
  createDiseaseLegend();
}

// Update the chart visibility based on the threshold value
function updateChartVisibility() {
  var threshold = parseInt(thresholdSlider.value);

  var visibleParents = nodes
    .filter(function (node) {
      return node.isParent;
    })
    .slice(0, threshold);

  nodes.forEach(function (node) {
    if (node.isParent) {
      node.hidden = !visibleParents.includes(node);
    } else {
      var parentLinks = links.filter(function (link) {
        return link.target.id === node.id;
      });
      node.hidden = !parentLinks.some(function (link) {
        return visibleParents.includes(link.source);
      });
    }
  });

  links.forEach(function (link) {
    link.hidden = link.source.hidden || link.target.hidden;
  });

  // Call updateAllFilters to update visibility based on new threshold
  updateAllFilters();
}

function hideNodeAndChildren(node) {
  node.hidden = true;

  var childLinks = links.filter(function (link) {
    return link.source.id === node.id;
  });

  var childNodes = childLinks.map(function (link) {
    return link.target;
  });

  childNodes.forEach(function (child) {
    var parentLinks = links.filter(function (link) {
      return link.target.id === child.id;
    });

    var allParentsHidden = parentLinks.every(function (link) {
      return link.source.hidden;
    });

    if (allParentsHidden) {
      hideNodeAndChildren(child);
    }
  });
}

d3.select("#redrawChart").on("click", function () {
  redrawChart(links);
});

function redrawChart1(originalLinks) {
  if (simulation) {
    //console.log("Simulation before restart: ", simulation);

    // Add nodes and links to the simulation and restart
    simulation.nodes(nodes).force("link").links(links);

    simulation.alpha(1).restart();

    //console.log("Simulation after restart: ", simulation);
  } else {
    //console.log("Simulation is not defined");
  }
}

function redrawChart(originalLinks) {
  if (simulation) {
    //console.log("Simulation before restart: ", simulation);

    // Unfix the node positions
    nodes.forEach(function (node) {
      node.fx = null;
      node.fy = null;
    });

    // Add nodes and links to the simulation and restart
    simulation.nodes(nodes).force("link").links(links);

    simulation.alpha(1).restart();

    // Add 'end' event listener to fix node positions when simulation ends
    simulation.on("end", function () {
      nodes.forEach(function (node) {
        node.fx = node.x;
        node.fy = node.y;
      });
    });

    //console.log("Simulation after restart: ", simulation);
  } else {
    console.log("Simulation is not defined");
  }
}

// Get color based on interaction type
// Get color based on interaction type
function getColor(type) {
  var lowercaseType = type.toLowerCase();

  // Check if the type is in the colorMap, if yes, return the corresponding color
  if (colorMap.hasOwnProperty(lowercaseType)) {
    return colorMap[lowercaseType];
  } else {
    // If the type is not in the colorMap, default to black
    return "black";
  }
}

var colorMap = {
  target: "green",
  enzyme: "blue",
  transporter: "red",
  carrier: "orange",
  unknown: "black",
  phase1: "steelblue", // Choose a different color
  phase2: "purple", // Choose a different color
  phase3: "cyan", // Choose a different color
  phase4: "magenta", // Choose a different color
};

// var Disease_colorMap_legend= {
//   Phase1: "green",
//   Phase2: "blue",
//   Phase3: "red",
//   Phase4: "orange"
// };
var hiddenInteractions = {
  target: false,
  enzyme: false,
  transporter: false,
  carrier: false,
  unknown: false,
  Phase1: false,
  Phase2: false,
  Phase3: false,
  Phase4: false,
};

//Legends Dragable code below
// Assuming you've imported D3 as d3
// Draggable functionality for the legend box

//Legends Dragable end code

// Create the legend for interactions
var interactions = [
  "Target",
  "Enzyme",
  "Transporter",
  "Carrier",
  "unknown",
  "Phase1",
  "Phase2",
  "Phase3",
  "Phase4",
];
//Legends Dragable code below
// Assuming you've imported D3 as d3
// Draggable functionality for the legend box

//Legends Dragable end code

// Create the legend for interactions
var interactions = [
  "Target",
  "Enzyme",
  "Transporter",
  "Carrier",
  "unknown",
  "Phase1",
  "Phase2",
  "Phase3",
  "Phase4",
];

//Legends Dragable code below
// Assuming you've imported D3 as d3
// Draggable functionality for the legend box

//Legends Dragable end code

// Create the legend for interactions
function createLegend() {
  var legendContent = d3.select("#legend-content");

  legendContent.selectAll("div").remove();

  var legendContent2 = d3.select("#legend-content_disease");
  legendContent2.selectAll("div").remove();

  var legendContent3 = d3.select("#trial_to_hide");
  legendContent3.selectAll("div").remove();

  //console.log("interaction legend",legendContent);
  //console.log("disease legend",legendContent2);

  var uniqueInteractions = [];

  links.forEach(function (link) {
    var interaction = link.type; // No need to convert to lowercase
    if (
      interactions.includes(
        interaction.charAt(0).toUpperCase() + interaction.slice(1)
      ) &&
      !uniqueInteractions.includes(interaction)
    ) {
      if (["Phase1", "Phase2", "Phase3", "Phase4"].includes(interaction)) {
        createLegendItem(interaction, getColor(interaction), legendContent2);
      } else {
        createLegendItem(interaction, getColor(interaction), legendContent);
      }
      uniqueInteractions.push(interaction);
    }
  });
  //console.log("unique Interactions", uniqueInteractions);
  function createLegendItem(interaction, color, container) {
    //console.log("CreateLegendItem", interaction +"\n"+color);
    //console.log("CreateLegendItem COntainer", container);

    var legendItem = container
      .append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("margin-bottom", "5px")
      .on("click", function () {
        d3.select(this).classed("selected-legend1", true);
      });
    //console.log("legendItem", legendItem);
    var phases = ["Phase1", "Phase2", "Phase3", "Phase4"];
    var dropdown = legendItem
      .append("div")
      .attr("class", "dropdown1")
      .style("position", "relative")
      .style("width", "20px")
      .style("height", "3px")
      // Adjust the height to control the line thickness
      .style("background-color", function () {
        if (!phases.includes(interaction)) {
          return color;
        }
      })
      .style("border-top", function () {
        if (phases.includes(interaction)) {
          return "3px dotted " + color;
        } else {
          return color;
        }
      })
      .on("click", function () {
        var clickedText = d3.select(this.parentNode).select("span");
        if (!clickedText.classed("text-through")) {
          var menu = d3.select(this).select(".dropdown-menu1");
          if (menu.style("display") === "none") {
            menu.style("display", "flex");
          } else {
            menu.style("display", "none");
          }
        }
      });

    var dropdownMenu = dropdown
      .append("div")
      .attr("class", "dropdown-menu1")
      .style("display", "none")
      .style("position", "absolute")
      .style("left", "25px")
      .style("height", "20px")
      .style("flex-direction", "row");

    for (var i = 0; i < interactions.length; i++) {
      var color = getColor(interactions[i]);
      dropdownMenu
        .append("div")
        .style("width", "20px")
        .style("height", "20px")
        .style("background-color", color)
        .on(
          "click",
          (function (selectedInteraction) {
            return function () {
              var selectedColor = getColor(selectedInteraction);
              var selectedLegendItem = d3.select(".selected-legend1");
              //console.log(selectedLegendItem, "selectedLegendItem");

              console.log(selectedColor, colorMap, "here are both");

              colorMap[interaction.toLowerCase()] = selectedColor;

              console.log(selectedColor, colorMap, "here are both");

              if (phases.includes(interaction)) {
                dropdown.style("border-top", `3px dotted ${selectedColor}`);
              } else if (!phases.includes(interaction)) {
                dropdown.style("background-color", selectedColor);
              }
              if (selectedLegendItem.node()) {
                // Check if the selection is not empty
                selectedLegendItem
                  .select(".dropdown-menu1")
                  .style("display", "none");
              }
              d3.selectAll(".selected-legend1").classed(
                "selected-legend1",
                false
              );
              redrawLinks();
            };
          })(interactions[i])
        );
    }

    var legendText = legendItem
      .append("span")
      .style("margin-left", "10px")
      .text(interaction);

    if (
      uniqueInteractions.includes("Phase1") ||
      uniqueInteractions.includes("Phase2") ||
      uniqueInteractions.includes("Phase3") ||
      uniqueInteractions.includes("Phase4")
    ) {
      legendContent3.style("display", "block");
    } else {
      legendContent3.style("display", "none");
      // Set display to "block" or any other desired value
    }

    // Event listener for the legend item text
    // Assuming that you have already defined the "nodes" and "links" arrays
    // and the "hiddenInteractions" object to track the visibility of interactions.
    legendText.on("click", function () {
      var clickedText = d3.select(this);
      var interaction = clickedText.text();

      if (clickedText.classed("text-through")) {
        clickedText.classed("text-through", false);
        hiddenInteractions[interaction] = false;
      } else {
        clickedText.classed("text-through", true);
        hiddenInteractions[interaction] = true;
      }

      updateAllFilters();
    });
  }

  document.addEventListener("click", function (event) {
    var dropdownMenus = d3.selectAll(".dropdown-menu1");
    dropdownMenus.each(function () {
      var menu = d3.select(this);
      if (
        menu.style("display") === "flex" &&
        !menu.empty() &&
        !d3.select(event.target).classed("selected-legend1") &&
        !d3.select(event.target.parentNode).classed("selected-legend1")
      ) {
        menu.style("display", "none");
      }
    });
    d3.selectAll(".selected-legend1").classed("selected-legend1", false);
  });
}

function drawLinks() {
  svg
    .selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("class", "link")
    .style("stroke", function (d) {
      return colorMap[d.type];
    }); // Use colorMap to get the color for the link type
  // ... rest of your link drawing code ...
}

// And here's the redrawLinks function
function redrawLinks() {
  // Update the 'stroke' style of the links using the updated colorMap
  //console.log(link)
  link.style("stroke", function (d) {
    console.log(
      d,
      d.type,
      colorMap,
      "Testinng Interaction :" + colorMap[d.type]
    );
    return colorMap[d.type.toLowerCase()];
  });
}

//Protein Class Color Map
var proteinColorMap = {
  Adhesion: "#ff7f0e",
  "Secreted protein": "#17becf",
  Enzyme: "#1f77b4",
  GPCR: "#2ca02c",
  "Membrane receptor": "#9467bd",
  Kinase: "#9467bd",
  Transporter: "#7f7f7f",
  Unknown: "#8c564b",
  "Epigenetic regulator": "black",
  "Structural protein": "#d62728",
  "Surface antigen": "#bcbd22",
  "Ion channel": "#d62728",
  "Transcription factor": "#2ca02c",
  "Nuclear receptor": "#ff7f0e",
};

function updateChildNodeColors() {
  d3.selectAll(".node circle").style("fill", function (d) {
    return proteinColorMap[d.Protein_Class] || "steelblue";
  });
}

function createProteinsLegend() {
  var hiddenProteins = {}; // Change this to hiddenProteinClasses
  var proteins = [
    "Adhesion",
    "Secreted protein",
    "Enzyme",
    "GPCR",
    "Membrane receptor",
    "Kinase",
    "Transporter",
    "Unknown",
    "Epigenetic regulator",
    "Structural protein",
    "Surface antigen",
    "Ion channel",
    "Transcription factor",
    "Nuclear receptor",
  ];
  var legendContent = d3.select("#legend_protein_status-content");
  legendContent.selectAll("div").remove();
  var uniqueProteins = new Set();

  links.forEach(function (link) {
    var proteinClass11 = link.target.Protein_Class; // No need to convert to lowercase
    //console.log(proteinClass11);

    if (
      proteins.includes(proteinClass11) &&
      !uniqueProteins.has(proteinClass11)
    ) {
      createLegendItem(proteinClass11, proteinColorMap[proteinClass11]);
      uniqueProteins.add(proteinClass11);
    }
  });
  /*
  proteins.forEach(function(protein) {
                    createLegendItem(protein, proteinColorMap[protein]);
  });
                */

  function createLegendItem(protein, color) {
    var legendItem = legendContent
      .append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("margin-bottom", "5px")
      .on("click", function () {
        d3.select(this).classed("selected-legend2", true);
      });

    var dropdown = legendItem
      .append("div")
      .attr("class", "dropdown2")
      .style("position", "relative")
      .style("width", "10px")
      .style("height", "10px")
      .style("background-color", color)
      .on("click", function () {
        var clickedText = d3.select(this.parentNode).select("span");
        if (!clickedText.classed("text-through")) {
          var menu = d3.select(this).select(".dropdown-menu2");
          if (menu.style("display") === "none") {
            menu.style("display", "flex");
          } else {
            menu.style("display", "none");
          }
        }
      });

    var dropdownMenu = dropdown
      .append("div")
      .attr("class", "dropdown-menu2")
      .style("display", "none")
      .style("position", "absolute")
      .style("left", "25px")
      .style("height", "20px")
      .style("flex-direction", "row");

    for (let i = 0; i < proteins.length; i++) {
      let color = proteinColorMap[proteins[i]];
      dropdownMenu
        .append("div")
        .style("width", "20px")
        .style("height", "20px")
        .style("background-color", color)
        .on(
          "click",
          (function (selectedProtein) {
            return function () {
              // d3.event.stopPropagation();  // Stop the click event from bubbling up to parent elements
              var selectedColor = proteinColorMap[selectedProtein];
              var selectedLegendItem = d3.select(".selected-legend2");
              proteinColorMap[protein] = selectedColor;
              dropdown.style("background-color", selectedColor);
              if (selectedLegendItem.node()) {
                selectedLegendItem
                  .select(".dropdown-menu2")
                  .style("display", "none");
              }
              d3.selectAll(".selected-legend2").classed(
                "selected-legend2",
                false
              );
              updateChildNodeColors();
            };
          })(proteins[i])
        );
    }

    var legendText = legendItem
      .append("span")
      .style("margin-left", "10px")
      .text(protein);

    // Assuming 'legendText' is a selection of the legend text elements
    // Assuming you have already created nodes, links, labels, and images in your chart

    legendText.on("click", function () {
      var clickedText = d3.select(this);
      var proteinClass = clickedText.text();

      if (clickedText.classed("text-through")) {
        clickedText.classed("text-through", false);
        hiddenProteinClasses[proteinClass] = false;
      } else {
        clickedText.classed("text-through", true);
        hiddenProteinClasses[proteinClass] = true;
      }

      updateAllFilters();
    });
  }

  document.addEventListener("click", function (event) {
    var dropdownMenus = d3.selectAll(".dropdown-menu2");
    dropdownMenus.each(function () {
      var menu = d3.select(this);
      if (
        menu.style("display") === "flex" &&
        !menu.empty() &&
        !d3.select(event.target).classed("selected-legend2") &&
        !d3.select(event.target.parentNode).classed("selected-legend2")
      ) {
        menu.style("display", "none");
      }
    });
    d3.selectAll(".selected-legend2").classed("selected-legend2", false);
  });
}

// color of the disease
let DiseaseColorMap = {
  "Congenital and Neonatal": "#FF5733",
  "Respiratory Tract": "#66CCCC",
  Cardiovascular: "#FF3333",
  "Nutritional and Metabolic": "#FFD700",
  Neoplasms: "#9932CC",
  "Mental Disorders": "#FF1493",
  Eye: "#00BFFF",
  "Behavior Mechanisms": "#32CD32",
  Infections: "#FF4500",
  "Digestive System": "#8B4513",
  "Pathological Conditions": "#FF6347",
  "Skin and Connective Tissue": "#FA8072",
  "Hemic and Lymphatic": "#800080",
  Female_Urogenital: "#FF69B4",
  "Nervous System": "#1E90FF",
  "Immune System": "#00FF00",
  "Chemically-Induced Disorders": "#FF8C00",
  Stomatognathic: "#FFDAB9",
  Musculoskeletal: "#B0E0E6",
  "Wounds and Injuries": "#8B0000",
  Otorhinolaryngologic: "#FFA500",
  "Endocrine System": "#FF7F50",
  "Male Urogenital": "#9932CC",
  "Occupational Diseases": "#2E8B57",
  "Genetic Inborn": "#4B0082",
};

// tag5
// funtion to the disease in the legend
function createDiseaseLegend() {
  var hiddendisease = {}; // Change this to
  var diseases = [
    "Congenital and Neonatal",
    "Respiratory Tract",
    "Cardiovascular",
    "Nutritional and Metabolic",
    "Neoplasms",
    "Mental Disorders",
    "Eye",
    "Behavior Mechanisms",
    "Infections",
    "Digestive System",
    "Pathological Conditions",
    "Skin and Connective Tissue",
    "Hemic and Lymphatic",
    "Female_Urogenital",
    "Nervous System",
    "Immune System",
    "Chemically-Induced Disorders",
    "Stomatognathic",
    "Musculoskeletal",
    "Wounds and Injuries",
    "Otorhinolaryngologic",
    "Endocrine System",
    "Male Urogenital",
    "Occupational Diseases",
    "Genetic Inborn",
  ];

  var legendContent = d3.select("#legend_disease_status-content");
  legendContent.selectAll("div").remove();
  // links.forEach(function (link) {
  //   for(let i=0 ; i<diseases.length ; i++){
  //     if(link.target.DiseaseClass === diseases[i])
  //     {
  //       console.log(link.target.DiseaseClass , "Disease_class");

  //     }

  //   }
  // })

  // links.forEach(function (link) {
  //   var diceaseClass11 = link.target.Protein_Class; // No need to convert to lowercase
  //   //console.log(proteinClass11);
  // for(let i=0 ; i<diseases.length ; i++){

  //   if (true) {

  //     createLegendItem(diseases[i], diseaseColors[i]);

  //   }

  // }
  var uniqueDisease = new Set();

  links.forEach(function (link) {
    var diseaseClass11 = link.target.DiseaseClass; // No need to convert to lowercase
    //console.log(proteinClass11);

    if (
      diseases.includes(diseaseClass11) &&
      !uniqueDisease.has(diseaseClass11)
    ) {
      //console.log(link.target.DiseaseClass);
      createLegendItem(
        diseaseClass11,
        DiseaseColorMap[diseaseClass11],
        diseaseClass11
      );
      uniqueDisease.add(diseaseClass11);
    }
  });

  function createLegendItem(disease, color, diseasetemp) {
    var legendItem = legendContent
      .append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("margin-bottom", "5px");

    var dropdown = legendItem
      .append("div")
      .attr("class", "triangle")
      .style("position", "relative")
      .style("width", "0")
      .style("height", "0")
      .style("border-left", "10px solid transparent")
      .style("border-right", "10px solid transparent")
      .style("border-bottom", "17px solid " + color)
      .style("border-radius", "0");

    var dropdownMenu = dropdown
      .append("div")
      .attr("class", "dropdown-menu2")
      .style("display", "none")
      .style("position", "absolute")
      .style("left", "25px")
      .style("height", "20px")
      .style("flex-direction", "row");

    for (let i = 0; i < diseases.length; i++) {
      dropdownMenu
        .append("div")
        .style("width", "20px")
        .style("height", "20px")
        .style("background-color", "red");
    }
    var legendText = legendItem
      .append("span")
      .style("margin-left", "10px")
      .text(disease);

    legendText.on("click", function () {
      var clickedText = d3.select(this);
      var diseaseClass = clickedText.text();

      if (clickedText.classed("text-through")) {
        clickedText.classed("text-through", false);
        hiddenDiseaseClasses[diseaseClass] = false;
      } else {
        clickedText.classed("text-through", true);
        hiddenDiseaseClasses[diseaseClass] = true;
      }

      updateAllFilters();
    });
  }

  // disable the change
  var legendContent4 = d3.select("#Disease_to_hide");

  if (diseases.some((disease) => uniqueDisease.has(disease))) {
    legendContent4.style("display", "block");
  } else {
    legendContent4.style("display", "none");
    console.log("check1");
    // Set display to "block" or any other desired value
  }
}

// var legendContent4 = d3.select("#Disease_to_hide");

//         if (diseases.some(disease => uniqueDisease.has(disease))) {
//           console.log(uniqueDisease, ' here are unique interactions');
//           console.log("check");
//           legendContent4.style("display", "block");
//         } else {
//           legendContent4.style("display", "none");
//           // Set display to "block" or any other desired value
//         }

// Call the function to create the legend
function createLegend_status() {
  var legendContent = d3.select("#legend_drug_status-content");
  legendContent.selectAll("div").remove();
  var drugStatusArray = [
    "Nutraceutical",
    "Experimental",
    "Investigational",
    "Approved",
    "Vet-approved",
    "Illicit",
  ];
  var uniqueDrugStatus = new Set();

  links.forEach(function (link) {
    var drugStatusClass11 = link.source.Drug_status;

    if (
      drugStatusArray.includes(drugStatusClass11) &&
      !uniqueDrugStatus.has(drugStatusClass11)
    ) {
      createLegendItem(drugStatusClass11, colorCodes[drugStatusClass11]);
      uniqueDrugStatus.add(drugStatusClass11);
    }
  });
  /*
  for (var status in colorCodes) {
                    createLegendItem(status, colorCodes[status]);
  }
                */

  function createLegendItem(status, color) {
    var legendItem = legendContent
      .append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("margin-bottom", "5px")
      .on("click", function () {
        d3.select(this).classed("legend-item-clicked", true); // Add a class to the clicked legend item
      });

    var dropdown = legendItem
      .append("div")
      .attr("class", "dropdown1")
      .style("position", "relative")
      .style("width", "25px")
      .style("height", "12px")
      .style("border-radius", "12px")
      .style("background-color", color)
      .on("click", function () {
        var clickedText = d3.select(this.parentNode).select("span");
        if (!clickedText.classed("text-through")) {
          var menu = d3.select(this).select(".dropdown-menu");
          if (menu.style("display") === "none") {
            menu.style("display", "flex");
          } else {
            menu.style("display", "none");
          }
        }
      });

    var dropdownMenu = dropdown
      .append("div")
      .attr("class", "dropdown-menu")
      .style("display", "none") // make sure the dropdown menu is hidden by default
      .style("position", "absolute")
      .style("left", "25px")
      .style("height", "20px")
      .style("flex-direction", "row");

    for (var color in colorPalette) {
      dropdownMenu
        .append("div")
        .style("width", "20px")
        .style("height", "20px")
        .style("background-color", color)
        .on(
          "click",
          (function (selectedColor) {
            return function () {
              colorCodes[status] = selectedColor;
              dropdown.style("background-color", selectedColor);
              //changeNodeImage(status, colorPalette[selectedColor]);
              //changeNodeImage(status, drugType, colorPalette[selectedColor]);
              changeNodeImage(status, selectedColor);
              dropdown.select(".dropdown-menu").style("display", "none"); // <--- This line hides the dropdown after color selection
              event.stopPropagation();
            };
          })(color)
        );
    }

    var legendText = legendItem
      .append("span")
      .style("margin-left", "10px") // reduce left margin from 30px to 10px
      .text(status);

    // Event listener for the legend item text
    legendText.on("click", function () {
      var clickedText = d3.select(this);
      var drugStatus = clickedText.text();

      if (clickedText.classed("text-through")) {
        clickedText.classed("text-through", false);
        hiddenDrugStatuses[drugStatus] = false;
      } else {
        clickedText.classed("text-through", true);
        hiddenDrugStatuses[drugStatus] = true;
      }
      updateAllFilters();
    });
  }

  // Event listener to close the dropdown menus when clicked anywhere on the webpage
  document.addEventListener("click", function (event) {
    var dropdownMenus = d3.selectAll(".dropdown-menu");
    dropdownMenus.each(function () {
      var menu = d3.select(this);
      if (
        menu.style("display") === "flex" &&
        !menu.empty() &&
        !d3.select(event.target).classed("legend-item-clicked") &&
        !d3.select(event.target.parentNode).classed("legend-item-clicked")
      ) {
        menu.style("display", "none");
      }
    });
    d3.selectAll(".legend-item-clicked").classed("legend-item-clicked", false); // Remove the class from all legend items
  });
}

function updateVisibility_legends() {
  // Update visibility of nodes
  d3.selectAll(".node").style("visibility", function (d) {
    // Hide or show parent nodes based on the drug status, drug type and interaction
    if (
      d.isParent &&
      (hiddenDrugStatuses[d.Drug_status] ||
        hiddenDrugTypes[d.Drug_type] ||
        links.some((l) => l.source.id === d.id && hiddenInteractions[l.type]))
    ) {
      return "hidden";
    }

    // Hide or show child nodes based on the protein class and interaction
    if (
      !d.isParent &&
      (hiddenProteinClasses[d.Protein_Class] ||
        links.some((l) => l.target.id === d.id && hiddenInteractions[l.type]))
    ) {
      return "hidden";
    }

    // If the node is neither hidden by drug status, protein class nor interaction
    return "visible";
  });

  // Update visibility of links
  d3.selectAll(".link").style("visibility", function (d) {
    // Hide or show links based on the interaction type, drug status, drug type, and protein class
    if (
      hiddenInteractions[d.type] ||
      hiddenDrugStatuses[d.source.Drug_status] ||
      hiddenDrugTypes[d.source.Drug_type] ||
      hiddenProteinClasses[d.target.Protein_Class]
    ) {
      return "hidden";
    }

    // If the link is neither hidden by interaction type, drug status, nor protein class
    return "visible";
  });
}

function changeNodeImage(status, selectedColor) {
  const newImagePath = colorPalette[selectedColor];
  const drugStatusIndex = newImagePath.match(/left(\d+)/)[1];

  d3.selectAll(".node-parent")
    .filter(function (node) {
      return node.Drug_status === status;
    })
    .each(function (node) {
      const drugType = node.Drug_type;

      // Fetch the current image path of the node
      let currentImagePath = d3.select(this).select("image").attr("xlink:href");

      // Extract drugTypeIndex from the current image path
      let drugTypeIndex = currentImagePath.match(/right(\d+)/)[1];

      const correctImagePath = `/static/d3/images/capsules/left${drugStatusIndex}right${drugTypeIndex}.png`;
      //console.log(correctImagePath);
      nodeImages[node.id] = correctImagePath;
      d3.select(this).select("image").attr("xlink:href", correctImagePath);
    });
}

function createLegend_drugType() {
  var legendContent = d3.select("#legend_drug_type-content");
  legendContent.selectAll("div").remove();
  var drugTypeArray = ["Biotech", "Small Molecule"];
  var uniqueDrugType = new Set();

  links.forEach(function (link) {
    var drugTypeClass11 = link.source.Drug_type;
    if (
      drugTypeArray.includes(drugTypeClass11) &&
      !uniqueDrugType.has(drugTypeClass11)
    ) {
      createLegendItem(drugTypeClass11, colorCodesDrugType[drugTypeClass11]);
      uniqueDrugType.add(drugTypeClass11);
    }
  });

  function createLegendItem(drugType, color) {
    console.log(legendContent, "legendContent");
    var legendItem = legendContent
      .append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("margin-bottom", "5px")
      .on("click", function () {
        d3.select(this).classed("legend-item-clicked", true); // Add a class to the clicked legend item
      });

    var dropdown = legendItem
      .append("div")
      .attr("class", "dropdown1")
      .style("position", "relative")
      .style("width", "25px")
      .style("height", "12px")
      .style("border-radius", "12px")
      .style("background-color", color)
      .on("click", function () {
        var clickedText = d3.select(this.parentNode).select("span");
        if (!clickedText.classed("text-through")) {
          var menu = d3.select(this).select(".dropdown-menu");
          if (menu.style("display") === "none") {
            menu.style("display", "flex");
          } else {
            menu.style("display", "none");
          }
        }
      });

    var dropdownMenu = dropdown
      .append("div")
      .attr("class", "dropdown-menu")
      .style("display", "none") // make sure the dropdown menu is hidden by default
      .style("position", "absolute")
      .style("left", "25px")
      .style("height", "20px")
      .style("flex-direction", "row");

    for (var color in colorPaletteDrugType) {
      dropdownMenu
        .append("div")
        .style("width", "20px")
        .style("height", "20px")
        .style("background-color", color)
        .on(
          "click",
          (function (selectedColor) {
            return function () {
              colorCodesDrugType[drugType] = selectedColor;
              dropdown.style("background-color", selectedColor);
              let newImagePath = colorCodesDrugType_images[selectedColor];
              //console.log(newImagePath)
              changeNodeImageForDrugType(drugType, selectedColor);
              dropdown.select(".dropdown-menu").style("display", "none");
              event.stopPropagation();
            };
          })(color)
        );
    }

    var legendText = legendItem
      .append("span")
      .style("margin-left", "10px")
      .text(drugType);

    legendText.on("click", function () {
      var clickedText = d3.select(this);
      var drugType = clickedText.text();

      if (clickedText.classed("text-through")) {
        clickedText.classed("text-through", false);
        hiddenDrugTypes[drugType] = false;
      } else {
        clickedText.classed("text-through", true);
        hiddenDrugTypes[drugType] = true;
      }

      updateAllFilters();
    });

    // TODO: You need to implement the event listener for the legend item text based on the drug type.
    // Refer to the existing legend for how to implement this part.
  }
}

function changeNodeImageForDrugType(drugType, selectedColor) {
  const newImagePath = colorCodesDrugType_images[selectedColor];
  const drugTypeIndex = newImagePath.match(/right(\d+)/)[1];

  d3.selectAll(".node-parent")
    .filter(function (node) {
      return node.Drug_type === drugType;
    })
    .each(function (node) {
      // Fetch the current image path of the node
      let currentImagePath = d3.select(this).select("image").attr("xlink:href");
      //console.log(currentImagePath)
      // Extract drugStatusIndex from the current image path
      let drugStatusIndex = currentImagePath.match(/left(\d+)/)[1];

      const correctImagePath = `/static/d3/images/capsules/left${drugStatusIndex}right${drugTypeIndex}.png`;
      //console.log(correctImagePath);
      nodeImages[node.id] = correctImagePath;
      d3.select(this).select("image").attr("xlink:href", correctImagePath);
    });
}

function updateAllFilters() {
  // child nodes
  // tag3 remove the new entry
  d3.selectAll(".node:not(.node-parent)")
    .selectAll("circle, text , path")
    .style("visibility", function (d) {
      if (d.hidden) {
        // if hidden by slider filter
        return "hidden";
      }

      var relatedLinks = links.filter((l) => l.target.id === d.id);
      var isHiddenBasedOnInteraction = relatedLinks.every(
        (l) => hiddenInteractions[l.type]
      );
      var isHiddenBasedOnProteinClass = hiddenProteinClasses[d.Protein_Class];

      var isHiddenBasedOnDiseaseClass = hiddenDiseaseClasses[d.DiseaseClass];
      // Hide if not connected to any parent
      if (relatedLinks.length === 0) {
        return "hidden";
      }

      // Check if all parents connected to this child are hidden
      // Check if all parents connected to this child are hidden
      var allParentsHidden = relatedLinks.every((l) => {
        var parentNode = nodes.find((n) => n.id === l.source.id && n.isParent);
        return (
          parentNode &&
          (hiddenDrugStatuses[parentNode.Drug_status] ||
            hiddenDrugTypes[parentNode.Drug_type] ||
            parentNode.hidden ||
            hiddenInteractions[l.type]) // Here we use the interaction type of the link
        );
      });
      // remove the child node only
      if (
        isHiddenBasedOnInteraction ||
        isHiddenBasedOnProteinClass ||
        isHiddenBasedOnDiseaseClass ||
        allParentsHidden
      ) {
        return "hidden";
      }
      return "visible";
    });

  // links
  link.style("visibility", function (d) {
    if (d.hidden) {
      // if hidden by slider filter
      return "hidden";
    }
    var isHiddenBasedOnInteraction = hiddenInteractions[d.type];
    var isHiddenBasedOnProteinClass =
      hiddenProteinClasses[d.target.Protein_Class];

    var isHiddenBasedOnDiseaseClass =
      hiddenDiseaseClasses[d.target.DiseaseClass];

    var isHiddenBasedOnDrugStatus = hiddenDrugStatuses[d.source.Drug_status];
    var isHiddenBasedOnDrugType = hiddenDrugTypes[d.source.Drug_type];

    // Adding visibility check for source and target nodes for the link.
    var isSourceNodeHidden = nodes.find((n) => n.id === d.source.id).hidden;
    var isTargetNodeHidden = nodes.find((n) => n.id === d.target.id).hidden;

    if (
      isHiddenBasedOnInteraction ||
      isHiddenBasedOnProteinClass ||
      isHiddenBasedOnDiseaseClass ||
      isHiddenBasedOnDrugStatus ||
      isHiddenBasedOnDrugType ||
      isSourceNodeHidden ||
      isTargetNodeHidden
    ) {
      return "hidden";
    }
    return "visible";
  });

  // parent nodes
  d3.selectAll(".node-parent").style("visibility", function (d) {
    if (d.hidden) {
      // if hidden by slider filter
      return "hidden";
    }
    var relatedLinks = links.filter((l) => l.source.id === d.id);
    var flag = true;
    link.filter(function (temp) {
      var isLinkVisible = d3.select(this).style("visibility");

      if (relatedLinks.includes(temp)) {
        if (isLinkVisible === "visible") {
          flag = false;
        }
      }
    });

    var anyVisibleChildren = relatedLinks.some(
      (l) =>
        !hiddenInteractions[l.type] &&
        !hiddenProteinClasses[
          nodes.find((n) => n.id === l.target.id).Protein_Class &&
            nodes.find((n) => n.id === l.target.id).DiseaseClass
        ]
    );

    var anyVisibledisease = relatedLinks.some(
      (l) =>
        !hiddenInteractions[l.type] &&
        !hiddenDiseaseClasses[
          nodes.find((n) => n.id === l.target.id).DiseaseClass
        ]
    );

    // Check Drug_status and Drug_type directly in the parent node
    var isHiddenBasedOnDrugStatus = hiddenDrugStatuses[d.Drug_status];
    var isHiddenBasedOnDrugType = hiddenDrugTypes[d.Drug_type];
    var isHiddenBasedOnInteraction = relatedLinks.every(
      (l) => hiddenInteractions[l.type]
    );
    var isHiddenBasedOnProteinClass = !anyVisibleChildren;
    var isHiddenBasedOnDiseaseClass = !anyVisibledisease;

    if (
      isHiddenBasedOnInteraction ||
      isHiddenBasedOnDrugStatus ||
      // isHiddenBasedOnProteinClass ||
      // isHiddenBasedOnDiseaseClass ||
      isHiddenBasedOnDrugType ||
      flag
    ) {
      return "hidden";
    }
    return "visible";
  });

  // hey
}

// Pull nodes towards the center
// Pull nodes towards the center
// Pull nodes towards the center
function pullToCenterParent11(width, height, strength, gap) {
  var centerX = width / 2;
  var centerY = height / 2;

  return function () {
    var parentNodes = nodes.filter(function (n) {
      return n.isParent;
    });
    for (var i = 0, n = parentNodes.length; i < n; ++i) {
      var node = parentNodes[i];
      var targetX = centerX + (i - n / 2) * gap;
      var targetY = centerY + (i - n / 2) * gap;

      node.vx += (targetX - node.x) * strength;
      node.vy += (targetY - node.y) * strength;
    }
  };
}

// Pull nodes towards the center
function pullToCenterParent(width, height, strength) {
  return function () {
    for (var i = 0, n = nodes.length; i < n; ++i) {
      var node = nodes[i];
      if (node.isParent) {
        var childNodes = nodes.filter(function (n) {
          return n.parent === node.id;
        });
        if (childNodes.length > 0) {
          var centerX = d3.mean(childNodes, function (n) {
            return n.x;
          });
          var centerY = d3.mean(childNodes, function (n) {
            return n.y;
          });

          node.vx += (centerX - node.x) * strength;
          node.vy += (centerY - node.y) * strength;
        }
      }
    }
  };
}

function pullToCenterChild(width, height, strength, gap) {
  return function () {
    for (var i = 0, n = nodes.length; i < n; ++i) {
      var node = nodes[i];
      if (!node.isParent) {
        var parent = nodes.find(function (n) {
          return n.id === node.parent;
        });
        if (parent) {
          var parentX = parent.x;
          var parentY = parent.y;
          var dx = parentX - node.x;
          var dy = parentY - node.y;
          var distance = Math.sqrt(dx * dx + dy * dy);
          var targetX =
            parentX + (dx / distance) * (parent.radius + gap + node.radius);
          var targetY =
            parentY + (dy / distance) * (parent.radius + gap + node.radius);

          // Adjust the target coordinates based on node radius and text bounding box
          var nodeText = node.isParent ? "" : node.id;
          var textBoundingBox = getTextBoundingBox(nodeText);
          var textWidth = textBoundingBox.width + 10;
          var textHeight = textBoundingBox.height + 10;
          var offsetX = textWidth / 2;
          var offsetY = textHeight / 2;

          targetX += node.x > parentX ? offsetX : -offsetX;
          targetY += node.y > parentY ? offsetY : -offsetY;

          node.vx += (targetX - node.x) * strength;
          node.vy += (targetY - node.y) * strength;
        }
      }
    }
  };
}

// Add boundary force to prevent nodes from going outside the chart area
function boundaryForce(width, height, padding) {
  return function () {
    for (var i = 0, n = nodes.length; i < n; ++i) {
      var node = nodes[i];
      var radius = node.isParent ? node.radius : node.radius + 5;
      var x = node.x + node.vx;
      var y = node.y + node.vy;

      if (x - radius < 0) {
        node.vx += radius - x + padding;
      } else if (x + radius > width) {
        node.vx -= x + radius - width + padding;
      }

      if (y - radius < 0) {
        node.vy += radius - y + padding;
      } else if (y + radius > height) {
        node.vy -= y + radius - height + padding;
      }
    }
  };
}

// Get the bounding box of a text element
function getTextBoundingBox(text) {
  var svg = d3.select("body").append("svg");
  var textElement = svg.append("text").text(text);
  var boundingBox = textElement.node().getBBox();
  svg.remove();
  return boundingBox;
}

// Drag event handlers
function drag(simulation) {
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  return d3
    .drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
}
let btn_count = 0;
d3.select("#GetmoreData").on("click", function () {
  clearGraph();
  btn_count++;
  document.getElementById("ManagePreviousState").style.display = "block";
  if (thredhold_value < 5 && child_nodes > 180) {
    slicedata = slicedata + 200;
  } else {
    if (thredhold_value <= 7) {
      numberofnodes = numberofnodes + 1;
      console.log("incease the number of nodes");
    } else if (thredhold_value > 7 && thredhold_value <= 14) {
      numberofnodes = numberofnodes + 2;
    } else if (thredhold_value > 14 && thredhold_value <= 50) {
      numberofnodes = numberofnodes + 6;
    } else if (thredhold_value > 50 && thredhold_value <= 150) {
      numberofnodes = numberofnodes + 20;
    } else if (thredhold_value > 150 && thredhold_value <= 300) {
      numberofnodes = numberofnodes + 50;
    } else if (thredhold_value > 300 && thredhold_value <= 600) {
      numberofnodes = numberofnodes + 100;
    } else if (thredhold_value >= 600) {
      numberofnodes = numberofnodes + 200;
    }
  }
  processData(numberofnodes, slicedata);
});

document.getElementById("ManagePreviousState").style.display = "none";

d3.select("#ManagePreviousState").on("click", function () {
  clearGraph();
  btn_count--;
  if (btn_count <= 0) {
    document.getElementById("ManagePreviousState").style.display = "none";
  }
  if (thredhold_value < 5 && child_nodes > 180) {
    slicedata -= 200;
  } else {
    if (thredhold_value <= 7) {
      numberofnodes -= 1;
    } else if (thredhold_value > 7 && thredhold_value <= 14) {
      numberofnodes -= 2;
    } else if (thredhold_value > 14 && thredhold_value <= 50) {
      numberofnodes -= 6;
    } else if (thredhold_value > 50 && thredhold_value <= 150) {
      numberofnodes -= 20;
    } else if (thredhold_value > 150 && thredhold_value <= 300) {
      numberofnodes -= 50;
    } else if (thredhold_value > 300 && thredhold_value <= 600) {
      numberofnodes -= 100;
    } else if (thredhold_value >= 600) {
      numberofnodes -= 200;
    }
  }
  processData(numberofnodes, slicedata);

  document.getElementById("GetmoreData").disabled = false;
  if (
    document.getElementById("GetmoreData").innerHTML === "Maximum data reached"
  ) {
    document.getElementById("GetmoreData").innerHTML = "Get more data";
  }
});

function clearGraph() {
  const svg = d3.select("#chart");
  svg.selectAll("*").remove();
  nodes = [];
  links = [];
}
