document.addEventListener("DOMContentLoaded", function () {
  fetch("/analytics/get-analytics-data")
    .then((response) => response.json())
    .then((data) => {
      var anomalies = data.anomalies;
      var alarmHistory = data.alarm_history;

      // Chart 1: Pie Chart for Anomaly Status Distribution
      var statusCounts = {};
      anomalies.forEach(function (item) {
        var status = item.status || "Unknown";
        statusCounts[status] = (statusCounts[status] || 0) + 1;
      });
      var statusLabels = Object.keys(statusCounts);
      var statusData = Object.values(statusCounts);

      var statusCtx = document.getElementById("statusChart").getContext("2d");
      new Chart(statusCtx, {
        type: "pie",
        data: {
          labels: statusLabels,
          datasets: [
            {
              label: "Anomaly Status Distribution",
              data: statusData,
              backgroundColor: [
                "rgba(255, 99, 132, 0.7)",
                "rgba(54, 162, 235, 0.7)",
                "rgba(255, 206, 86, 0.7)",
                "rgba(75, 192, 192, 0.7)",
                "rgba(153, 102, 255, 0.7)",
              ],
              borderColor: [
                "rgba(255, 99, 132, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(255, 206, 86, 1)",
                "rgba(75, 192, 192, 1)",
                "rgba(153, 102, 255, 1)",
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: "Anomaly Status Distribution" },
          },
        },
      });

      // Chart 2: Line Chart for Anomaly Trend Over Time
      var trendData = {};
      anomalies.forEach(function (item) {
        var date = new Date(item.timestamp);
        var monthYear = date.getFullYear() + "-" + (date.getMonth() + 1);
        trendData[monthYear] = (trendData[monthYear] || 0) + 1;
      });
      var trendLabels = Object.keys(trendData).sort();
      var trendCounts = trendLabels.map((label) => trendData[label]);

      var trendCtx = document.getElementById("trendChart").getContext("2d");
      new Chart(trendCtx, {
        type: "line",
        data: {
          labels: trendLabels,
          datasets: [
            {
              label: "Anomalies Over Time",
              data: trendCounts,
              fill: false,
              borderColor: "rgba(75, 192, 192, 1)",
              tension: 0.1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: "Anomaly Trend Over Time" },
          },
        },
      });

      // Chart 3: Bar Chart for Alarm History by Room
      var alarmCounts = {};
      alarmHistory.forEach(function (item) {
        var room = item.room;
        alarmCounts[room] = (alarmCounts[room] || 0) + 1;
      });
      var alarmLabels = Object.keys(alarmCounts);
      var alarmDataValues = Object.values(alarmCounts);

      var alarmCtx = document.getElementById("alarmChart").getContext("2d");
      new Chart(alarmCtx, {
        type: "bar",
        data: {
          labels: alarmLabels,
          datasets: [
            {
              label: "Alarms Triggered",
              data: alarmDataValues,
              backgroundColor: "rgba(153, 102, 255, 0.7)",
              borderColor: "rgba(153, 102, 255, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: "Alarm History by Room" },
          },
          scales: { y: { beginAtZero: true } },
        },
      });

      // Chart 4: Bar Chart for Average Anomaly Duration by Status
      var durationSums = {};
      var durationCounts = {};
      anomalies.forEach(function (item) {
        if (item.duration) {
          var status = item.status || "Unknown";
          durationSums[status] = (durationSums[status] || 0) + item.duration;
          durationCounts[status] = (durationCounts[status] || 0) + 1;
        }
      });
      var avgDuration = {};
      Object.keys(durationSums).forEach(function (status) {
        avgDuration[status] = durationSums[status] / durationCounts[status];
      });
      var durationLabels = Object.keys(avgDuration);
      var durationData = Object.values(avgDuration);

      var durationCtx = document
        .getElementById("durationChart")
        .getContext("2d");
      new Chart(durationCtx, {
        type: "bar",
        data: {
          labels: durationLabels,
          datasets: [
            {
              label: "Avg Anomaly Duration (sec) by Status",
              data: durationData,
              backgroundColor: "rgba(255, 159, 64, 0.7)",
              borderColor: "rgba(255, 159, 64, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: {
              display: true,
              text: "Average Anomaly Duration by Status",
            },
          },
          scales: { y: { beginAtZero: true } },
        },
      });

      // Chart 5: Bar Chart for Anomaly Confidence Distribution (using bins)
      var bins = { "0-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0 };
      anomalies.forEach(function (item) {
        var conf = parseFloat(item.confidence);
        if (!isNaN(conf)) {
          if (conf < 0.5) bins["0-0.5"]++;
          else if (conf < 0.7) bins["0-0.7"]++;
          else if (conf < 0.9) bins["0-0.9"]++;
          else bins["0-1.0"]++;
        }
      });
      var confidenceLabels = Object.keys(bins);
      var confidenceData = Object.values(bins);

      var confidenceCtx = document
        .getElementById("confidenceChart")
        .getContext("2d");
      new Chart(confidenceCtx, {
        type: "bar",
        data: {
          labels: confidenceLabels,
          datasets: [
            {
              label: "Anomaly Confidence Distribution",
              data: confidenceData,
              backgroundColor: "rgba(255, 205, 86, 0.7)",
              borderColor: "rgba(255, 205, 86, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: { display: true, text: "Anomaly Confidence Distribution" },
          },
          scales: { y: { beginAtZero: true } },
        },
      });

      // Chart 6: Bar Chart for Average Alarm Duration by Room
      var alarmDurationSums = {};
      var alarmDurationCounts = {};
      alarmHistory.forEach(function (item) {
        if (item.duration) {
          var room = item.room;
          alarmDurationSums[room] =
            (alarmDurationSums[room] || 0) + item.duration;
          alarmDurationCounts[room] = (alarmDurationCounts[room] || 0) + 1;
        }
      });
      var avgAlarmDuration = {};
      Object.keys(alarmDurationSums).forEach(function (room) {
        avgAlarmDuration[room] =
          alarmDurationSums[room] / alarmDurationCounts[room];
      });
      var alarmDurationLabels = Object.keys(avgAlarmDuration);
      var alarmDurationData = Object.values(avgAlarmDuration);

      var alarmDurationCtx = document
        .getElementById("alarmDurationChart")
        .getContext("2d");
      new Chart(alarmDurationCtx, {
        type: "bar",
        data: {
          labels: alarmDurationLabels,
          datasets: [
            {
              label: "Avg Alarm Duration (sec) by Room",
              data: alarmDurationData,
              backgroundColor: "rgba(54, 162, 235, 0.7)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: {
              display: true,
              text: "Average Alarm Duration by Room",
            },
          },
          scales: { y: { beginAtZero: true } },
        },
      });
    })
    .catch((error) => {
      console.error("Error fetching analytics data:", error);
    });
});
