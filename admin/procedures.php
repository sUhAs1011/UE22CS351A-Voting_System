<?php
// Include the database connection
include 'includes/conn.php';

// Execute the stored procedure
$result = $conn->query("CALL GetPositionsWithCandidateCount()");

if (!$result) {
    die("Error executing the procedure: " . $conn->error);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Procedure Output</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #F1E9D2; /* Set the background color */
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
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
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
            color: #ffffff;
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
        <!-- Back Button -->
        <a href="home.php" class="back-button">← Back to Home</a>

        <h2>Positions with Candidate Count</h2>

        <!-- Table to display procedure output -->
        <table>
            <thead>
                <tr>
                    <th>Position ID</th>
                    <th>Position Description</th>
                    <th>Candidate Count</th>
                </tr>
            </thead>
            <tbody>
                <?php
                // Loop through the results and display them in a table
                while ($row = $result->fetch_assoc()) {
                    echo "<tr>
                            <td>{$row['PositionID']}</td>
                            <td>{$row['PositionDescription']}</td>
                            <td>{$row['CandidateCount']}</td>
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
$conn->close();
?>
