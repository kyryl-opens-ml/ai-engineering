// Create a container div with specific styling for the visualization
const vizContainer = d3.select(container)
    .append("div")
    .style("width", "100%")
    .style("height", "600px")
    .style("font-family", "Helvetica, Arial, sans-serif")
    .style("background", "#ffffff");

// 1. Data Extraction & Processing (Since the PDF is Lorem Ipsum text, we analyze letter frequency)
// The raw text from the PDF
const rawText = `Sample PDF This is a simple PDF file. Fun fun fun. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Phasellus facilisis odio sed mi. Curabitur suscipit. Nullam vel nisi. Etiam semper ipsum ut lectus. Proin aliquam, erat eget pharetra commodo, eros mi condimentum quam, sed commodo justo quam ut velit. Integer a erat. Cras laoreet ligula cursus enim. Aenean scelerisque velit et tellus. Vestibulum dictum aliquet sem. Nulla facilisi. Vestibulum accumsan ante vitae elit. Nulla erat dolor, blandit in, rutrum quis, semper pulvinar, enim. Nullam varius congue risus. Vivamus sollicitudin, metus ut interdum eleifend, nisi tellus pellentesque elit, tristique accumsan eros quam et risus. Suspendisse libero odio, mattis sit amet, aliquet eget, hendrerit vel, nulla. Sed vitae augue. Aliquam erat volutpat. Aliquam feugiat vulputate nisl. Suspendisse quis nulla pretium ante pretium mollis. Proin velit ligula, sagittis at, egestas a, pulvinar quis, nisl. Pellentesque sit amet lectus. Praesent pulvinar, nunc quis iaculis sagittis, justo quam lobortis tortor, sed vestibulum dui metus venenatis est. Nunc cursus ligula. Nulla facilisi. Phasellus ullamcorper consectetuer ante. Duis tincidunt, urna id condimentum luctus, nibh ante vulputate sapien, id sagittis massa orci ut enim. Pellentesque vestibulum convallis sem. Nulla consequat quam ut nisl. Nullam est. Curabitur tincidunt dapibus lorem. Proin velit turpis, scelerisque sit amet, iaculis nec, rhoncus ac, ipsum. Phasellus lorem arcu, feugiat eu, gravida eu, consequat molestie, ipsum. Nullam vel est ut ipsum volutpat feugiat. Aenean pellentesque. In mauris. Pellentesque dui nisi, iaculis eu, rhoncus in, venenatis ac, ante. Ut odio justo, scelerisque vel, facilisis non, commodo a, pede. Cras nec massa sit amet tortor volutpat varius. Donec lacinia, neque a luctus aliquet, pede massa imperdiet ante, at varius lorem pede sed sapien. Fusce erat nibh, aliquet in, eleifend eget, commodo eget, erat. Fusce consectetuer. Cras risus tortor, porttitor nec, tristique sed, convallis semper, eros. Fusce vulputate ipsum a mauris. Phasellus mollis. Curabitur sed urna. Aliquam nec sapien non nibh pulvinar convallis. Vivamus facilisis augue quis quam. Proin cursus aliquet metus. Suspendisse lacinia. Nulla at tellus ac turpis eleifend scelerisque. Maecenas a pede vitae enim commodo interdum. Donec odio. Sed sollicitudin dui vitae justo. Morbi elit nunc, facilisis a, mollis a, molestie at, lectus. Suspendisse eget mauris eu tellus molestie cursus. Duis ut magna at justo dignissim condimentum. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus varius. Ut sit amet diam suscipit mauris ornare aliquam. Sed varius. Duis arcu. Etiam tristique massa eget dui. Phasellus congue. Aenean est erat, tincidunt eget, venenatis quis, commodo at, quam.`;

// Count letter frequencies
const counts = {};
const letters = rawText.toLowerCase().replace(/[^a-z]/g, "").split("");
letters.forEach(l => counts[l] = (counts[l] || 0) + 1);

// Convert to array and sort
const data = Object.entries(counts)
    .map(([letter, frequency]) => ({ letter: letter.toUpperCase(), frequency }))
    .sort((a, b) => b.frequency - a.frequency);

// 2. Set up SVG dimensions
const margin = { top: 60, right: 30, bottom: 60, left: 60 };
const width = vizContainer.node().getBoundingClientRect().width - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

const svg = vizContainer.append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// 3. Title and Subtitle
svg.append("text")
    .attr("x", width / 2)
    .attr("y", -30)
    .attr("text-anchor", "middle")
    .style("font-size", "22px")
    .style("font-weight", "bold")
    .style("fill", "#333")
    .text("Latin Text Composition Analysis");

svg.append("text")
    .attr("x", width / 2)
    .attr("y", -10)
    .attr("text-anchor", "middle")
    .style("font-size", "14px")
    .style("fill", "#666")
    .text("Letter frequency distribution in the 'Sample PDF' document");

// 4. Scales
const x = d3.scaleBand()
    .domain(data.map(d => d.letter))
    .range([0, width])
    .padding(0.2);

const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.frequency)])
    .nice()
    .range([height, 0]);

const colorScale = d3.scaleSequential()
    .domain([0, d3.max(data, d => d.frequency)])
    .interpolator(d3.interpolateBlues);

// 5. Axes
svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("font-size", "12px");

svg.append("g")
    .call(d3.axisLeft(y));

// Axis labels
svg.append("text")
    .attr("text-anchor", "middle")
    .attr("x", width / 2)
    .attr("y", height + 40)
    .style("fill", "#555")
    .text("Character");

svg.append("text")
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("y", -40)
    .attr("x", -height / 2)
    .style("fill", "#555")
    .text("Frequency Count");

// 6. Bars with interaction
const bars = svg.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("x", d => x(d.letter))
    .attr("y", height) // Start at bottom for animation
    .attr("width", x.bandwidth())
    .attr("height", 0) // Start with 0 height
    .attr("fill", d => colorScale(d.frequency))
    .attr("rx", 3) // Rounded corners top
    .style("cursor", "pointer");

// Animation
bars.transition()
    .duration(800)
    .delay((d, i) => i * 50)
    .attr("y", d => y(d.frequency))
    .attr("height", d => height - y(d.frequency));

// 7. Tooltip functionality
const tooltip = vizContainer.append("div")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background-color", "rgba(0,0,0,0.8)")
    .style("color", "white")
    .style("padding", "8px 12px")
    .style("border-radius", "4px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("z-index", "10");

bars.on("mouseover", function(event, d) {
    d3.select(this).attr("fill", "#ff7f0e"); // Highlight color
    tooltip.style("visibility", "visible")
           .html(`<strong>${d.letter}</strong>: ${d.frequency} occurrences<br/>${((d.frequency/letters.length)*100).toFixed(1)}% of total`);
})
.on("mousemove", function(event) {
    // Get mouse position relative to container
    const [mx, my] = d3.pointer(event, vizContainer.node());
    tooltip.style("top", (my - 10) + "px")
           .style("left", (mx + 15) + "px");
})
.on("mouseout", function(event, d) {
    d3.select(this).attr("fill", colorScale(d.frequency));
    tooltip.style("visibility", "hidden");
});

// 8. Add a text stats box
const totalChars = letters.length;
const topChar = data[0];
const uniqueChars = data.length;

const statsBox = svg.append("g")
    .attr("transform", `translate(${width - 200}, 20)`);

statsBox.append("rect")
    .attr("width", 190)
    .attr("height", 80)
    .attr("fill", "#f8f9fa")
    .attr("stroke", "#ddd")
    .attr("rx", 5);

statsBox.append("text")
    .attr("x", 15)
    .attr("y", 25)
    .style("font-size", "12px")
    .style("font-weight", "bold")
    .text("Document Statistics:");

statsBox.append("text")
    .attr("x", 15)
    .attr("y", 45)
    .style("font-size", "11px")
    .text(`Total Characters: ${totalChars}`);

statsBox.append("text")
    .attr("x", 15)
    .attr("y", 65)
    .style("font-size", "11px")
    .text(`Most Common: '${topChar.letter}' (${topChar.frequency})`);
