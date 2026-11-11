
import { useEffect, useState } from "react";
import Papa from "papaparse";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // CSV upload states
  const [fileName, setFileName] = useState("");
  const [rows, setRows] = useState([]);
  const [columns, setColumns] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // API states
  const [customers, setCustomers] = useState([]);
  const [offers, setOffers] = useState([]);
  const [allocationSummary, setAllocationSummary] = useState(null);

  const [apiError, setApiError] = useState("");
  const [apiLoading, setApiLoading] = useState(true);

  // Fetch all dashboard data from FastAPI
  useEffect(() => {
    const fetchDashboardData = async () => {
      setApiLoading(true);
      setApiError("");

      try {
        const [effectsResponse, offersResponse, summaryResponse] =
          await Promise.all([
            fetch(`${API_URL}/api/customer-effects`),
            fetch(`${API_URL}/api/optimized-offers`),
            fetch(`${API_URL}/api/allocation-summary`),
          ]);

        if (!effectsResponse.ok) {
          throw new Error("Unable to fetch customer treatment effects.");
        }

        if (!offersResponse.ok) {
          throw new Error("Unable to fetch optimized discount offers.");
        }

        if (!summaryResponse.ok) {
          throw new Error("Unable to fetch allocation summary.");
        }

        const effectsData = await effectsResponse.json();
        const offersData = await offersResponse.json();
        const summaryData = await summaryResponse.json();

        setCustomers(effectsData);
        setOffers(offersData);
        setAllocationSummary(summaryData);
      } catch (err) {
        setApiError(
          err.message || "Unable to connect to the Python backend."
        );
      } finally {
        setApiLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Upload and validate CSV
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

  // Calculate missing cells in uploaded CSV
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

  // Identify treatment effect columns
  const effectColumns =
    customers.length > 0
      ? Object.keys(customers[0]).filter((column) =>
          column.startsWith("effect_")
        )
      : [];

  return (
    <div className="app">
      {/* Sidebar */}
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

          <a className="nav-item" href="#optimization">
            Optimization
          </a>

          <a className="nav-item" href="#about">
            About Project
          </a>
        </nav>

        <div className="sidebar-footer">
          Week 2 · Causal ML
        </div>
      </aside>

      {/* Main Dashboard */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CAUSAL AI PLATFORM</p>
            <h1 id="overview">Campaign Dashboard</h1>
          </div>

          <span className="status">Prototype</span>
        </header>

        {/* Welcome Section */}
        <section className="welcome">
          <div>
            <h2>Welcome to EconoCausal</h2>

            <p>
              Analyze customer campaign data, estimate discount
              effects, and explore personalized discount strategies.
            </p>
          </div>
        </section>

        {/* API Loading and Error Messages */}
        {apiLoading && (
          <p className="api-loading">
            Loading dashboard data from Python backend...
          </p>
        )}

        {apiError && (
          <div className="error-message" role="alert">
            Backend Error: {apiError}

            <p>
              Check that FastAPI is running and that the required
              output CSV files exist.
            </p>
          </div>
        )}

        {/* Dashboard Statistics */}
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
            <span>Loaded from causal API</span>
          </div>
        </section>

        {/* CSV Upload */}
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

        {/* Customer Data Preview */}
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

        {/* Customer Treatment Effects */}
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

        {/* Discount Allocation Summary */}
        <section className="panel" id="summary">
          <div className="section-heading">
            <div>
              <h2>Discount Allocation Summary</h2>
              <p>
                Overall results from the discount optimization model.
              </p>
            </div>
          </div>

          {allocationSummary && (
            <div className="stats-grid">
              <div className="stat-card">
                <p>Total Customers</p>
                <h2>
                  {Number(
                    allocationSummary.total_customers ?? 0
                  ).toLocaleString()}
                </h2>
              </div>

              <div className="stat-card">
                <p>Total Discount Cost</p>
                <h2>
                  {Number(
                    allocationSummary.total_discount_cost ?? 0
                  ).toLocaleString()}
                </h2>
              </div>

              <div className="stat-card">
                <p>Expected Incremental Benefit</p>
                <h2>
                  {Number(
                    allocationSummary.expected_incremental_benefit ?? 0
                  ).toFixed(2)}
                </h2>
              </div>
            </div>
          )}

          {!apiLoading && !apiError && !allocationSummary && (
            <p>Allocation summary is not available.</p>
          )}
        </section>

        {/* Optimized Discount Offers */}
        <section className="panel" id="optimization">
          <div className="section-heading">
            <div>
              <h2>Optimized Discount Offers</h2>

              <p>
                Customer-specific discount recommendations generated
                by the optimization model.
              </p>
            </div>
          </div>

          {!apiLoading && !apiError && offers.length === 0 && (
            <p>
              No optimized offers available. Run the discount
              optimization script and check the Python API.
            </p>
          )}

          {offers.length > 0 && (
            <>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Customer ID</th>
                      <th>Previous Spend</th>
                      <th>Recommended Discount</th>
                      <th>Expected Incremental Benefit</th>
                    </tr>
                  </thead>

                  <tbody>
                    {offers.slice(0, 50).map((offer, index) => (
                      <tr key={offer.customer_id || index}>
                        <td>{offer.customer_id}</td>

                        <td>
                          {Number(offer.previous_spend).toFixed(2)}
                        </td>

                        <td>{offer.recommended_discount}</td>

                        <td>
                          {Number(
                            offer.expected_incremental_benefit
                          ).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p>
                Showing up to 50 of {offers.length} optimized customer offers.
              </p>
            </>
          )}
        </section>

        {/* About Project */}
        <section className="panel" id="about">
          <h2>Project Objectives</h2>

          <div className="objectives">
            <p>✓ Customer data preparation and cleaning</p>
            <p>✓ Exploratory data analysis</p>
            <p>✓ Causal DAG definition using DoWhy</p>
            <p>✓ Causal model training with EconML</p>
            <p>✓ React dashboard connected to Python API</p>
            <p>✓ Personalized discount optimization</p>
          </div>

          <p className="disclaimer">
            Treatment effects are model estimates, not guarantees
            of customer behavior. Purchase lift alone does not
            establish profitability.
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
