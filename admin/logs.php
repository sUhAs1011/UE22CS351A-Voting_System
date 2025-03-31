<?php
// Include the database connection (adjust the path as needed)
include 'includes/conn.php'; // Ensure this file has your DB connection details

// Query to fetch the audit logs
$query = "SELECT log_id, position_id, description, action_time FROM position_audit_log ORDER BY action_time DESC";
$result = mysqli_query($conn, $query);

if (!$result) {
    die("Error fetching logs: " . mysqli_error($conn));
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Position Audit Logs</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #F1E9D2; /* Page-wide background color */
            margin: 0;
            padding: 0;
        }
        .container {
            margin: 20px;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        h2 {
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #132237;
            color: #ffffff;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .back-button {
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background-color: #ebb723;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
        }
        .back-button:hover {
            background-color: #c7951c;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Back to Home Button -->
        <a href="home.php" class="back-button">← Back to Home</a>

        <h2>Position Audit Logs</h2>
        <table>
            <thead>
                <tr>
                    <th>Log ID</th>
                    <th>Position ID</th>
                    <th>Description</th>
                    <th>Action Time</th>
                </tr>
            </thead>
            <tbody>
                <?php
                // Fetch and display each row from the result
                while ($row = mysqli_fetch_assoc($result)) {
                    echo "<tr>
                            <td>" . $row['log_id'] . "</td>
                            <td>" . $row['position_id'] . "</td>
                            <td>" . htmlspecialchars($row['description']) . "</td>
                            <td>" . $row['action_time'] . "</td>
                        </tr>";
                }
                ?>
            </tbody>
        </table>
    </div>
</body>
</html>

<?php
// Close the database connection
mysqli_close($conn);
?>
