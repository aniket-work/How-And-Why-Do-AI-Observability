import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import _ from 'lodash';

const NetworkDashboard = () => {
  const [data, setData] = useState(null);
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await window.fs.readFile('network_stats.sql', { encoding: 'utf8' });
        const stats = JSON.parse(response);
        setData(stats);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="p-6 space-y-6 bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Network Security Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Event Types Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Event Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <PieChart width={400} height={300}>
              <Pie
                data={data.eventTypes}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                label
              >
                {data.eventTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </CardContent>
        </Card>

        {/* Risk Levels Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Levels Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart width={400} height={300} data={data.riskTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="high" stroke="#ff0000" />
              <Line type="monotone" dataKey="medium" stroke="#ffaa00" />
              <Line type="monotone" dataKey="low" stroke="#00aa00" />
            </LineChart>
          </CardContent>
        </Card>

        {/* Protocol Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Protocol Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <BarChart width={400} height={300} data={data.protocols}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </CardContent>
        </Card>

        {/* Event Frequency */}
        <Card>
          <CardHeader>
            <CardTitle>Event Frequency</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart width={400} height={300} data={data.frequency}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="events" stroke="#82ca9d" />
            </LineChart>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NetworkDashboard;