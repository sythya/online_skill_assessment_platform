import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/analytics/")
      .then((res) => {
        if (!res.ok) throw new Error("API error");
        return res.json();
      })
      .then((json) => setData(json))
      .catch(() => setError("Failed to load analytics"));
  }, []);

  if (error) return <h2>{error}</h2>;
  if (!data) return <h2>Loading analytics...</h2>;

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>Analytics Dashboard</h1>

      <h3>Total Attempts: {data.total_attempts}</h3>

      <hr />

      {/* Skill-wise Bar Chart */}
      <h2>Skill-wise Performance</h2>

      <BarChart
        width={600}
        height={300}
        data={data.skill_wise}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="skill_name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="correct" fill="#4CAF50" name="Correct Answers" />
        <Bar dataKey="total" fill="#2196F3" name="Total Questions" />
      </BarChart>

      <hr />

      {/* Difficulty-wise Pie Chart */}
      <h2>Difficulty-wise Performance</h2>

      <PieChart width={400} height={300}>
        <Pie
          data={data.difficulty_wise}
          dataKey="correct"
          nameKey="difficulty"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >
          {data.difficulty_wise.map((entry, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}

export default App;
