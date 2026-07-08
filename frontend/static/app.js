const api = "";

let currentTab = "users";

let graph = null;

let cache = {};

const objectList = document.getElementById("objectList");

const details = document.getElementById("details");

const title = document.getElementById("listTitle");

const search = document.getElementById("search");

const refresh = document.getElementById("refresh");

const tabs = document.querySelectorAll(".tab");

// ----------------------------------------------------
// Initialization
// ----------------------------------------------------

window.onload = () => {
  loadTab(currentTab);
};

refresh.onclick = () => {
  cache = {};

  loadTab(currentTab);
};

tabs.forEach((tab) => {
  tab.onclick = () => {
    tabs.forEach((t) => t.classList.remove("active"));

    tab.classList.add("active");

    currentTab = tab.dataset.tab;

    title.innerText = tab.innerText;

    loadTab(currentTab);
  };
});

// ----------------------------------------------------
// Search
// ----------------------------------------------------

search.onkeyup = () => {
  const value = search.value.toLowerCase();

  const items = objectList.querySelectorAll("li");

  items.forEach((item) => {
    if (item.innerText.toLowerCase().includes(value)) {
      item.style.display = "block";
    } else {
      item.style.display = "none";
    }
  });
};

// ----------------------------------------------------
// Load Tab
// ----------------------------------------------------

async function loadTab(tab) {
  details.innerHTML = "Loading...";

  objectList.innerHTML = "";

  destroyGraph();

  let endpoint = "/api/" + tab;

  if (cache[endpoint]) {
    renderList(tab, cache[endpoint]);

    return;
  }

  const response = await fetch(api + endpoint);

  const data = await response.json();

  cache[endpoint] = data;

  renderList(tab, data);
}

// ----------------------------------------------------
// Render List
// ----------------------------------------------------

function renderList(tab, data) {
  objectList.innerHTML = "";

  details.innerHTML = "Select an object.";

  data.forEach((item) => {
    const li = document.createElement("li");

    if (item.namespace) {
      li.innerHTML = item.namespace + " / " + item.name;
    } else {
      li.innerHTML = item.name;
    }

    li.onclick = () => {
      document
        .querySelectorAll("#objectList li")
        .forEach((x) => x.classList.remove("active"));

      li.classList.add("active");

      loadDetails(tab, item);
    };

    objectList.appendChild(li);
  });
}

// ----------------------------------------------------
// Destroy Graph
// ----------------------------------------------------

function destroyGraph() {
  if (graph) {
    graph.destroy();

    graph = null;
  }

  document.getElementById("graph").innerHTML = "";
}
// ----------------------------------------------------
// Load Details
// ----------------------------------------------------

async function loadDetails(tab, item) {
  let endpoint = "";

  switch (tab) {
    case "users":
      endpoint = "/api/user/" + encodeURIComponent(item.name);
      break;

    case "groups":
      endpoint = "/api/group/" + encodeURIComponent(item.name);
      break;

    case "serviceaccounts":
      endpoint =
        "/api/serviceaccount/" +
        encodeURIComponent(item.namespace) +
        "/" +
        encodeURIComponent(item.name);
      break;

    case "roles":
      endpoint =
        "/api/role/" +
        encodeURIComponent(item.namespace) +
        "/" +
        encodeURIComponent(item.name);
      break;

    case "clusterroles":
      endpoint = "/api/clusterrole/" + encodeURIComponent(item.name);
      break;

    case "rolebindings":
      showRoleBinding(item);
      return;

    case "clusterrolebindings":
      showClusterRoleBinding(item);
      return;

    default:
      return;
  }

  const response = await fetch(api + endpoint);

  const data = await response.json();

  renderDetails(tab, data);

  if (data.graph) {
    renderGraph(data.graph);
  }
}

// ----------------------------------------------------
// Render Details
// ----------------------------------------------------

function renderDetails(tab, data) {
  details.innerHTML = "";

  const card = document.createElement("div");

  card.className = "card";

  let obj = data.details || data.user || data.role || data.clusterRole;

  if (!obj) {
    details.innerHTML = "<h3>No data available</h3>";

    return;
  }

  let html = "";

  html += "<h3>" + obj.name + "</h3>";

  if (obj.namespace) {
    html += "<p><b>Namespace:</b> " + obj.namespace + "</p>";
  }

  if (obj.kind) {
    html += "<p><b>Kind:</b> " + obj.kind + "</p>";
  }

  card.innerHTML = html;

  details.appendChild(card);

  // ----------------------------------------------------
  // Permissions
  // ----------------------------------------------------

  if (obj.permissions) {
    const permissionCard = document.createElement("div");

    permissionCard.className = "card";

    permissionCard.innerHTML = "<h3>Permissions</h3>";

    obj.permissions.forEach((rule) => {
      const permission = document.createElement("div");

      permission.className = "permission";

      let ruleHtml = "";

      ruleHtml += "<h4>" + (rule.resources || []).join(", ") + "</h4>";

      (rule.verbs || []).forEach((v) => {
        ruleHtml += "<span>" + v + "</span>";
      });

      permission.innerHTML = ruleHtml;

      permissionCard.appendChild(permission);
    });

    details.appendChild(permissionCard);
  }

  // ----------------------------------------------------
  // RoleBindings
  // ----------------------------------------------------

  if (obj.roleBindings) {
    const rb = document.createElement("div");

    rb.className = "card";

    rb.innerHTML = "<h3>RoleBindings</h3>";

    obj.roleBindings.forEach((binding) => {
      rb.innerHTML += `
<p>
<b>${binding.name}</b><br>
Namespace : ${binding.namespace}<br>
Role : ${binding.role}
</p>
<hr>
`;
    });

    details.appendChild(rb);
  }

  // ----------------------------------------------------
  // ClusterRoleBindings
  // ----------------------------------------------------

  if (obj.clusterRoleBindings) {
    const crb = document.createElement("div");

    crb.className = "card";

    crb.innerHTML = "<h3>ClusterRoleBindings</h3>";

    obj.clusterRoleBindings.forEach((binding) => {
      crb.innerHTML += `
<p>
<b>${binding.name}</b><br>
Role : ${binding.role}
</p>
<hr>
`;
    });

    details.appendChild(crb);
  }
}
// ----------------------------------------------------
// Graph
// ----------------------------------------------------

function renderGraph(data) {
  destroyGraph();

  graph = cy({
    container: document.getElementById("graph"),

    elements: [
      ...data.nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
        },
      })),

      ...data.edges.map((edge) => ({
        data: {
          source: edge.source,
          target: edge.target,
        },
      })),
    ],

    style: [
      {
        selector: "node",

        style: {
          label: "data(label)",

          "text-valign": "center",

          "text-halign": "center",

          color: "#ffffff",

          "font-size": "12px",

          "font-weight": "bold",

          width: "55px",

          height: "55px",

          "background-color": "#2563eb",

          "text-wrap": "wrap",

          "text-max-width": "80px",
        },
      },

      {
        selector: 'node[type="User"]',

        style: {
          "background-color": "#2563eb",
        },
      },

      {
        selector: 'node[type="Group"]',

        style: {
          "background-color": "#059669",
        },
      },

      {
        selector: 'node[type="ServiceAccount"]',

        style: {
          "background-color": "#dc2626",
        },
      },

      {
        selector: 'node[type="Role"]',

        style: {
          "background-color": "#d97706",
        },
      },

      {
        selector: 'node[type="ClusterRole"]',

        style: {
          "background-color": "#7c3aed",
        },
      },

      {
        selector: 'node[type="RoleBinding"]',

        style: {
          "background-color": "#0891b2",

          shape: "round-rectangle",
        },
      },

      {
        selector: 'node[type="ClusterRoleBinding"]',

        style: {
          "background-color": "#be185d",

          shape: "round-rectangle",
        },
      },

      {
        selector: "edge",

        style: {
          width: 2,

          "curve-style": "bezier",

          "target-arrow-shape": "triangle",

          "line-color": "#94a3b8",

          "target-arrow-color": "#94a3b8",
        },
      },
    ],

    layout: {
      name: "breadthfirst",

      directed: true,

      padding: 40,

      spacingFactor: 1.5,
    },
  });

  graph.fit();
}

// ----------------------------------------------------
// RoleBinding Details
// ----------------------------------------------------

function showRoleBinding(item) {
  destroyGraph();

  details.innerHTML = "";

  let html = "";

  html += "<div class='card'>";

  html += "<h3>" + item.name + "</h3>";

  html += "<p><b>Namespace:</b> " + item.namespace + "</p>";

  html += "<p><b>Role:</b> " + item.role + "</p>";

  html += "</div>";

  html += "<div class='card'>";

  html += "<h3>Subjects</h3>";

  (item.subjects || []).forEach((subject) => {
    html += "<p>";

    html += "<b>" + subject.kind + "</b><br>";

    html += subject.name;

    if (subject.namespace) {
      html += "<br>" + subject.namespace;
    }

    html += "</p><hr>";
  });

  html += "</div>";

  details.innerHTML = html;
}

// ----------------------------------------------------
// ClusterRoleBinding Details
// ----------------------------------------------------

function showClusterRoleBinding(item) {
  destroyGraph();

  details.innerHTML = "";

  let html = "";

  html += "<div class='card'>";

  html += "<h3>" + item.name + "</h3>";

  html += "<p><b>ClusterRole:</b> " + item.role + "</p>";

  html += "</div>";

  html += "<div class='card'>";

  html += "<h3>Subjects</h3>";

  item.subjects.forEach((subject) => {
    html += "<p>";

    html += "<b>" + subject.kind + "</b><br>";

    html += subject.name;

    if (subject.namespace) {
      html += "<br>" + subject.namespace;
    }

    html += "</p><hr>";
  });

  html += "</div>";

  details.innerHTML = html;
}
