import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function TaskStatsChart({ data }) {
  const chartData = [
    { name: 'Completed', value: data.completed_tasks || 0, fill: '#10b981' },
    { name: 'Pending', value: data.pending_tasks || 0, fill: '#f59e0b' },
    { name: 'Overdue', value: data.overdue_tasks || 0, fill: '#ef4444' },
  ];

  // Avoid overlapping labels by using small padding and placing labels outside
  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            dataKey="value"
            outerRadius={80}
            innerRadius={40}
            paddingAngle={6}
            labelLine={false}
            label={({ cx, cy, midAngle, outerRadius, name, value }) => {
              if (value === 0) return null; // ✅ hide zero values

              const RADIAN = Math.PI / 180;
              const radius = outerRadius + 20;
              const x = cx + radius * Math.cos(-midAngle * RADIAN);
              const y = cy + radius * Math.sin(-midAngle * RADIAN);

              return (
                <text
                  x={x}
                  y={y}
                  fill="#333"
                  textAnchor={x > cx ? "start" : "end"}
                  dominantBaseline="central"
                  style={{ fontSize: 12 }}
                >
                  {name}: {value}
                </text>
              );
            }}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PriorityChart({ data }) {
  const chartData = [
    { name: 'High', value: data.high || 0 },
    { name: 'Medium', value: data.medium || 0 },
    { name: 'Low', value: data.low || 0 },
  ];
  const maxVal = Math.max(...chartData.map((d) => d.value), 1);

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} domain={[0, maxVal]} />
          <Tooltip />
          <Bar dataKey="value" fill="#0084ff" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
