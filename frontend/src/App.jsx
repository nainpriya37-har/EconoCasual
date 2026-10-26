
import { useEffect, useState } from "react";
import Papa from "papaparse";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [fileName, setFileName] = useState("");
  const [rows, setRows] = useState([]);
  const [columns, setColumns] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [customers, setCustomers] = useState([]);
  const [apiError, setApiError] = useState("");
  const [apiLoading, setApiLoading] = useState(true);

  // Fetch customer-level causal effects from the Python API.
  useEffect(() => {
    fetch(`${API_URL}/api/customer-effects`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Customer effects are unavailable. Run the causal training script first."
          );
        }
        return response.json();
      })
      .then((data) => {
        setCustomers(data);
        setApiError("");
      })
      .catch((err) => {
        setApiError(err.message);
      })
      .finally(() => {
        setApiLoading(false);
      });
  }, []);

  // Upload and validate the customer campaign CSV.
  function handleFileUpload(event) {
    const file = event.target.files?.[0];

    setError("");
    setRows([]);
    setColumns([]);
    setFileName("");

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please upload a CSV file.");
      return;
    }

    setLoading(true);
    setFileName(file.name);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,

      complete: (result) => {
        const parsedRows = result.data;
        const parsedColumns = result.meta.fields || [];

        const requiredColumns = [
          "customer_id",
          "age",
          "past_purchases",
          "loyalty_score",
          "previous_spend",
          "discount",
          "purchased",
          "revenue",
        ];

        const missingColumns = requiredColumns.filter(
          (column) => !parsedColumns.includes(column)
        );

        if (result.errors.length > 0) {
          setError(`CSV parsing issue: ${result.errors[0].message}`);
          setLoading(false);
          return;
        }

        if (missingColumns.length > 0) {
          setError(
            `Missing required columns: ${missingColumns.join(", ")}`
          );
          setLoading(false);
          return;
        }

        if (parsedRows.length === 0) {
          setError("The CSV contains no customer records.");
          setLoading(false);
          return;
        }

        setColumns(parsedColumns);
        setRows(parsedRows);
        setLoading(false);
      },

      error: () => {
        setError("Unable to read the CSV file.");
        setLoading(false);
      },
    });
  }

  const missingCells = rows.reduce((total, row) => {
    return (
      total +
      columns.filter(
        (column) =>
          row[column] === null ||
          row[column] === undefined ||
          String(row[column]).trim() === ""
      ).length
    );
  }, 0);

  // Find treatment-effect columns dynamically.
  const effectColumns =
    customers.length > 0
      ? Object.keys(customers[0]).filter((column) =>
          column.startsWith("effect_")
        )
      : [];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">E</div>
          <div>
            <h2>EconoCausal</h2>
            <p>Marketing Intelligence</p>
          </div>
        </div>

        <nav>
          <a className="nav-item active" href="#overview">
            Overview
          </a>
          <a className="nav-item" href="#upload">
            Data Upload
          </a>
          <a className="nav-item" href="#preview">
            Customer Data
          </a>
          <a className="nav-item" href="#effects">
            Causal Effects
          </a>
          <a className="nav-item" href="#about">
            About Project
          </a>
        </nav>

        <div className="sidebar-footer">
          Week 2 · Causal ML
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CAUSAL AI PLATFORM</p>
            <h1 id="overview">Campaign Dashboard</h1>
          </div>
          <span className="status">Prototype</span>
        </header>

        <section className="welcome">
          <div>
            <h2>Welcome to EconoCausal</h2>
            <p>
              Analyze customer campaign data, estimate discount
              effects, and explore personalized discount strategies.
            </p>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <p>Uploaded Customers</p>
            <h2>{rows.length.toLocaleString()}</h2>
            <span>Records in uploaded CSV</span>
          </div>

          <div className="stat-card">
            <p>Dataset Columns</p>
            <h2>{columns.length}</h2>
            <span>Detected fields</span>
          </div>

          <div className="stat-card">
            <p>Missing Cells</p>
            <h2>{missingCells.toLocaleString()}</h2>
            <span>In uploaded records</span>
          </div>

          <div className="stat-card">
            <p>Effect Records</p>
            <h2>{customers.length.toLocaleString()}</h2>
            <span>Loaded from the causal API</span>
          </div>
        </section>

        <section className="panel" id="upload">
          <div className="section-heading">
            <div>
              <h2>Upload Campaign Dataset</h2>
              <p>
                Select customer_campaigns.csv to preview and validate
                your customer data.
              </p>
            </div>
          </div>

          <label className="upload-area">
            <div className="upload-icon">↑</div>
            <h3>Choose a CSV file</h3>
            <p>Click here to browse files on your computer.</p>
            <span className="upload-button">Browse CSV</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileUpload}
            />
          </label>

          {fileName && (
            <p className="file-name">
              Selected file: <strong>{fileName}</strong>
            </p>
          )}

          {loading && <p>Reading CSV file...</p>}

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}
        </section>

        <section className="panel" id="preview">
          <div className="section-heading">
            <div>
              <h2>Customer Data Preview</h2>
              <p>
                {rows.length > 0
                  ? `Showing ${Math.min(rows.length, 10)} of ${rows.length} records.`
                  : "Upload a dataset to preview customer records."}
              </p>
            </div>
          </div>

          {rows.length > 0 && (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(0, 10).map((row, index) => (
                    <tr key={row.customer_id || index}>
                      {columns.map((column) => (
                        <td key={column}>{row[column] ?? ""}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="panel" id="effects">
          <div className="section-heading">
            <div>
              <h2>Customer-Level Treatment Effects</h2>
              <p>
                Estimated purchase-probability differences for
                alternative discount options versus the baseline.
              </p>
            </div>
          </div>

          {apiLoading && <p>Loading customer treatment effects...</p>}

          {!apiLoading && apiError && (
            <div className="error-message" role="alert">
              {apiError}
              <p>
                Ensure the Python API is running and the training
                script has generated outputs/customer_effects.csv.
              </p>
            </div>
          )}

          {!apiLoading && !apiError && customers.length === 0 && (
            <p>No customer effect records are available yet.</p>
          )}

          {customers.length > 0 && (
            <>
              <p>
                Loaded {customers.length} customer records and{" "}
                {effectColumns.length} estimated effect columns.
              </p>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {Object.keys(customers[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {customers.slice(0, 50).map((customer, index) => (
                      <tr key={index}>
                        {Object.entries(customer).map(([key, value]) => (
                          <td key={key}>
                            {typeof value === "number" &&
                            key.startsWith("effect_")
                              ? value.toFixed(4)
                              : String(value ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p>
                Showing up to 50 of {customers.length} customer records.
                Positive effects indicate estimated purchase lift;
                negative effects indicate estimated decrease.
              </p>
            </>
          )}
        </section>

        <section className="panel" id="about">
          <h2>Project Objectives</h2>
          <div className="objectives">
            <p>✓ Customer data preparation and cleaning</p>
            <p>✓ Exploratory data analysis</p>
            <p>✓ Causal DAG definition using DoWhy</p>
            <p>✓ Causal model training with EconML</p>
            <p>✓ React dashboard connected to the Python API</p>
          </div>
          <p className="disclaimer">
            Treatment effects are model estimates, not guarantees of
            customer behavior. Purchase lift alone does not establish
            profitability.
          </p>
        </section>

        <footer>
          EconoCausal · Dynamic Pricing via Double Machine Learning
        </footer>
      </main>
    </div>
  );
}

export default App;
