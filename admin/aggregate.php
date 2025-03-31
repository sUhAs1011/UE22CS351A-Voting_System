<?php
// Include necessary files and database connection
include_once 'includes/conn.php';

try {
    // SQL query to get total votes per position
    $sql = "
        SELECT 
            positions.description AS position,
            COUNT(votes.id) AS total_votes
        FROM 
            votes
        JOIN 
            positions ON votes.position_id = positions.id
        GROUP BY 
            positions.id;
    ";

    // Execute the query
    $result = $conn->query($sql);

    // Start HTML output
    echo "<div class='container' style='margin-top: 20px;'>"; // Start the main container
    
    // Add a background color to the body so the whole page is styled
    echo "<style>body { background-color: #F1E9D2; }</style>";
    
    // Back Button (same as in your procedure output page)
    echo "<a href='home.php' class='back-button' style='display: inline-block; margin-bottom: 20px; padding: 10px 20px; background-color: #ebb723; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 16px;'>← Back to Home</a>";
    
    // Check if there are results
    if ($result->num_rows > 0) {
        // Title and votes tally header
        echo "<div class='row' style='color:black; font-size: 17px; font-family: Times; text-align: center;'>";
        echo "<div class='col-xs-12'>";
        echo "<h3><b>VOTES TALLY</b></h3>";
        echo "</div></div>";
        
        // Display the results in a table
        echo "<div class='row' style='font-family: Times; justify-content: center;'>"; // Centering the row
        echo "<div class='col-lg-8'>"; // Limit the width of the table to 8 columns
        echo "<table class='table table-bordered' style='background-color: #f4f4f4; border: 1px solid #ddd; text-align: center;'>";
        echo "<thead style='background-color: #4682B4; color: white;'>";
        echo "<tr><th>Position</th><th>Total Votes</th></tr>";
        echo "</thead>";
        echo "<tbody>";
        
        // Loop through the results and display them
        while ($row = $result->fetch_assoc()) {
            echo "<tr>";
            echo "<td>" . htmlspecialchars($row['position']) . "</td>";
            echo "<td>" . htmlspecialchars($row['total_votes']) . "</td>";
            echo "</tr>";
        }
        
        echo "</tbody>";
        echo "</table>";
        echo "</div>";
        echo "</div>";
    } else {
        // If no votes are found
        echo "<div class='alert alert-warning' style='color:black; font-family: Times; font-size: 16px; text-align: center;'>
                No votes found.
              </div>";
    }
    echo "</div>"; // Close container
} catch (Exception $e) {
    // Handle any exceptions
    echo "<div class='alert alert-danger' style='color:black; font-family: Times; font-size: 16px; text-align: center;'>
            Error: " . $e->getMessage() . "
          </div>";
}

// Close the database connection
$conn->close();
?>
