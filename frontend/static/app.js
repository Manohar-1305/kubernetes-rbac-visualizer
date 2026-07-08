let cy = null;

async function loadGraph() {
  const response = await fetch("/api/graph");

  const data = await response.json();

  const elements = [];

  data.nodes.forEach((node) => {
    elements.push({
      data: {
        id: node.id,

        label: node.label,

        kind: node.kind,

        namespace: node.namespace,
      },
    });
  });

  data.edges.forEach((edge) => {
    elements.push({
      data: {
        source: edge.source,

        target: edge.target,

        relation: edge.relation,
      },
    });
  });

  if (cy) {
    cy.destroy();
  }

  cy = cytoscape({
    container: document.getElementById("cy"),

    elements: elements,

    layout: {
      name: "breadthfirst",
      directed: true,
      padding: 20,
    },

    style: [
      {
        selector: "node",

        style: {
          label: "data(label)",

          "text-valign": "center",

          "text-halign": "center",

          width: 55,

          height: 55,

          "font-size": 11,
        },
      },

      {
        selector: "edge",

        style: {
          "curve-style": "bezier",

          "target-arrow-shape": "triangle",

          label: "data(relation)",

          "font-size": 9,
        },
      },
    ],
  });

  cy.on("tap", "node", function (evt) {
    const node = evt.target;

    document.getElementById("details").innerHTML = `Name : ${node.data("label")}

Kind : ${node.data("kind")}

Namespace : ${node.data("namespace") ?? "Cluster"}`;
  });
}

loadGraph();
