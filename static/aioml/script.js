document.addEventListener("DOMContentLoaded", () => {
// The above line ensures that the script runs after the DOM is fully loaded


  // This is the event listener (Acts like a function that gets called when button is clicked)
  // Somehow these are better than using the onclick and others


document.getElementById('uploadBtn').addEventListener('click', async () => {
  const input = document.getElementById('csvInput');
  const file = input.files[0];
  
  if (!file) return alert("Choose a CSV!");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/aioml/file-submit", {
    method: "POST",
    body: formData
  });

  if (!response.ok) return alert("Upload failed!");
  
  const data = await response.json();

  // Show preview
  document.getElementById("previewHead").innerHTML = `<h4>🧾 Head</h4>${data.dfHead}`;
  document.getElementById("previewInfo").innerHTML = `<h4>ℹ️ Info</h4><pre>${data.dfInfo}</pre>`;
  document.getElementById("previewDescribe").innerHTML = `<h4>📊 Describe</h4>${data.dfDescribe}`;
  document.getElementById("dataPreviewSection").style.display = "block";
  document.getElementById("treatingMissingValues").style.display = "block";
});
  

// Analyze and treat missing values 'checkMissingValues'
document.getElementById('checkMissingValues').addEventListener('click', async () => {
  const response = await fetch("/aioml/missing-values", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ action: "check" })
  });

  const data = await response.json();
  const missingTable = data.missingTable; // e.g., { Age: 177, Cabin: 687 }

  if (!missingTable || Object.keys(missingTable).length === 0) {
    console.log("No missing values found.");
    document.getElementById("ViewingMissingValues").style.display = "block";
    document.getElementById('missingValuesCount').innerHTML = "<p>No missing values found.</p>";
    return;
  }

  // Show the section
  document.getElementById("ViewingMissingValues").style.display = "block";

  // Show count table
  let countTable = `<table border="1" cellpadding="6"><tr><th>Column</th><th>Missing Count</th></tr>`;
  for (const [col, count] of Object.entries(missingTable)) {
    countTable += `<tr><td>${col}</td><td>${count}</td></tr>`;
  }
  countTable += "</table>";
  document.getElementById("missingValuesCount").innerHTML = countTable;

  // Show treatment options
  let treatmentHTML = "";
  for (const col of Object.keys(missingTable)) {
    treatmentHTML += `
      <div style="margin-bottom: 1rem;">
        <strong>${col}</strong><br>
        <label><input type="radio" name="${col}" value="drop" /> Drop rows</label><br>
        <label><input type="radio" name="${col}" value="mean" /> Fill with mean</label><br>
        <label><input type="radio" name="${col}" value="median" /> Fill with median</label><br>
        <label><input type="radio" name="${col}" value="mode" /> Fill with mode</label><br>
      </div>
    `;
  }

  document.getElementById("selectMethod").innerHTML = treatmentHTML;
  document.getElementById("dataPreviewSection").style.display = "none";
  // document.getElementById("previewDescribe").style.display = "none";
  // Save globally for Apply use
  window._missingColumns = Object.keys(missingTable);
});

document.getElementById('handleMissingBtn').addEventListener('click', async () => {
  const treatments = {};

  try{
    for (const col of window._missingColumns) {
      const selected = document.querySelector(`input[name="${col}"]:checked`);
      if (selected) {
        treatments[col] = selected.value;
      }
    }

    if (Object.keys(treatments).length === 0) {
      alert("Please select at least one treatment.");
      return;
    }

    const response = await fetch("/aioml/missing-values", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ action: "treat", columns: treatments })
    });

    const result = await response.json(); 
    console.log(result);
    document.getElementById("downloadProcessedData").style.display = "block";
    document.getElementById("newDataFrame").innerHTML = result.newDFHead;
    document.getElementById("treatingMissingValues").style.display = "none";
    document.getElementById("downloadBtn").classList.remove("hidden");
    document.getElementById("downloadBtn").href = result.pathToNewFile;
    document.getElementById("viewingNewDF").style.display = "block";
  }
  catch (error) {
    document.getElementById("viewingNewDF").style.display = "block";  
  }

  
});

// 'doEncoding'
    document.getElementById('doEncoding').addEventListener('click',async () => {
          // Get the columns to encode
          const response = await fetch('/aioml/categorical-columns');
          const data = await response.json();
          const categoricalCols = data.categorical_columns;
  
          const container = document.getElementById("viewColumns");
          container.innerHTML = '';
          categoricalCols.forEach(col => {
              const checkbox = `<label><input type="checkbox" name="categoricalCols" value="${col}">${col}</label><br>`;
              container.innerHTML += checkbox;
          });
      document.getElementById("oneHotEncoding").style.display = "block";
    });
// 'encodeBtn'
    document.getElementById('encodeBtn').addEventListener('click', async () => {
      document.getElementById("viewColumns").style.display = "none";
      const selectedCols = [...document.querySelectorAll("input[name='categoricalCols']:checked")].map(e => e.value); 
  
      const response = await fetch("/aioml/one-hot-encode", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({ columns: selectedCols })
      });
  
      const data = await response.json();
      document.getElementById("encodedDataFrame").innerHTML = data.encodedDF;
      document.getElementById("downloadBtn").style.display = "inline-block";
      document.getElementById("viewingNewDF").style.display = "none";
      document.getElementById("encodeBtn").style.display = "none";
      document.getElementById("downloadBtn").href = data.pathToEncodedFile;

      document.getElementById("scaling").style.display = "block";
      await loadNumericalColumns();
  });


// Load numerical columns for normalization
  async function loadNumericalColumns() {
    const response = await fetch("/aioml/numerical-columns");
    const data = await response.json();
    const container = document.getElementById("numericalColumns");
    container.innerHTML = '';
    if (data.numerical_columns && data.numerical_columns.length > 0) {
      data.numerical_columns.forEach(col => {
        const checkbox = `
          <label>
            <input type="checkbox" name="numericalCols" value="${col}">
            📊 ${col}
          </label><br>`;
        container.innerHTML += checkbox;
      });
    } else {
      container.innerHTML = "<p>No numerical columns found.</p>";
    }
  }

  //  Send selected columns to normalize
  document.getElementById("normalize").addEventListener("click", async () => {
    document.getElementById("oneHotEncoding").style.display = "none";
    document.getElementById("numericalColumns").style.display = "none";
    const selected = Array.from(document.querySelectorAll("input[name='numericalCols']:checked")).map(input => input.value);
    const response = await fetch("/aioml/normalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ columns: selected })
    });
    const data = await response.json();
    document.getElementById("downloadBtn").href = data.pathToNormalizedFile;
    document.getElementById("normalizedResult").innerHTML = data.normalizedDF;
    document.getElementById("featureSelection").style.display = "inline-block";
    loadFeatureSelection()
  })

  // Load feature selection options
  async function loadFeatureSelection() {
    const response = await fetch("/aioml/features");
    const data = await response.json();
    const container = document.getElementById("featureList");
    container.innerHTML = '';
  
    if (data.features && data.features.length > 0) {
      data.features.forEach(col => {
        const checkbox = `
          <label>
            <input type="checkbox" name="featureCols" value="${col}">
             ${col}
          </label><br>`;
        container.innerHTML += checkbox;
      });
      document.getElementById("featureSelection").style.display = "block";
    } else {
      container.innerHTML = "<p>No features found.</p>";
    }
  }
  // Handle feature selection
  document.getElementById("featureSelectionButton").addEventListener("click", async () => {
    document.getElementById("scaling").style.display = "none";
    const selected = Array.from(document.querySelectorAll("input[name='featureCols']:checked"))
                          .map(input => input.value);
  
    const response = await fetch("/aioml/select-features", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features: selected })
    });
  
    const data = await response.json();
    document.getElementById("selectedDF").innerHTML = data.selectedDF;
    document.getElementById("downloadBtn").href = data.pathToSelected;
  })
  document.getElementById("themeToggle").addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    const isLight = document.body.classList.contains("light-mode");
    document.getElementById("themeToggle").textContent = isLight ? "🌙 Dark Mode" : "☀ Light Mode";
  });
  

})