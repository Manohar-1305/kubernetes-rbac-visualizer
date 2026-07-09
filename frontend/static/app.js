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

    search.value = "";

    destroyGraph();

    loadTab(currentTab);
  };
});

// ----------------------------------------------------
// Search
// ----------------------------------------------------

search.onkeyup = () => {
  const value = search.value.toLowerCase();

  document.querySelectorAll("#objectList li").forEach((li) => {
    li.style.display = li.innerText.toLowerCase().includes(value)
      ? "block"
      : "none";
  });
};

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
// Load Tab
// ----------------------------------------------------

async function loadTab(tab) {
  objectList.innerHTML = "";

  details.innerHTML = "Loading...";

  destroyGraph();

  const endpoint = "/api/" + tab;

  let data;

  if (cache[endpoint]) {
    data = cache[endpoint];
  } else {
    try {
      const response = await fetch(api + endpoint);

      data = await response.json();

      cache[endpoint] = data;
    } catch {
      details.innerHTML = "<h3>Unable to contact backend.</h3>";

      return;
    }
  }

  renderList(tab, data);
}
// ----------------------------------------------------
// Render List
// ----------------------------------------------------

function renderList(tab, data) {
  objectList.innerHTML = "";

  details.innerHTML = "Select an object.";

  if (!Array.isArray(data) || data.length === 0) {
    objectList.innerHTML = "<li>No objects found.</li>";

    return;
  }

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
// Load Details
// ----------------------------------------------------

async function loadDetails(tab, item) {
  destroyGraph();

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

  if (data.graph && data.graph.nodes && data.graph.nodes.length > 0) {
    renderGraph(data.graph);
  }
}
// ----------------------------------------------------
// Render Details
// ----------------------------------------------------

function renderDetails(tab, data) {
  details.innerHTML = "";

  const obj = data.details || data.user || data.role || data.clusterRole;

  if (!obj) {
    details.innerHTML = "<h3>No details available.</h3>";

    return;
  }

  // ----------------------------------------------------
  // Basic Information
  // ----------------------------------------------------

  const info = document.createElement("div");

  info.className = "card";

  let html = "";

  html += `<h3>${obj.name}</h3>`;

  if (obj.namespace) {
    html += `<p><b>Namespace:</b> ${obj.namespace}</p>`;
  }

  if (obj.kind) {
    html += `<p><b>Kind:</b> ${obj.kind}</p>`;
  }

  info.innerHTML = html;

  details.appendChild(info);

  // ----------------------------------------------------
  // Permissions
  // ----------------------------------------------------

  if (obj.permissions && obj.permissions.length > 0) {
    const permissionCard = document.createElement("div");

    permissionCard.className = "card";

    permissionCard.innerHTML = "<h3>Permissions</h3>";

    obj.permissions.forEach((rule) => {
      const permission = document.createElement("div");

      permission.className = "permission";

      permission.innerHTML = `

<h4>${(rule.resources || []).join(", ") || "*"}</h4>

<p><b>API Groups:</b>
${(rule.apiGroups || []).join(", ") || "-"}</p>

<p><b>Verbs:</b>
${(rule.verbs || []).join(", ")}</p>

`;

      permissionCard.appendChild(permission);
    });

    details.appendChild(permissionCard);
  } else {
    const empty = document.createElement("div");

    empty.className = "card";

    empty.innerHTML = "<h3>Permissions</h3><p>No permissions found.</p>";

    details.appendChild(empty);
  }

  // ----------------------------------------------------
  // RoleBindings
  // ----------------------------------------------------

  if (obj.roleBindings && obj.roleBindings.length > 0) {
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
}
// ----------------------------------------------------
// ClusterRoleBindings
// ----------------------------------------------------

if (obj.clusterRoleBindings && obj.clusterRoleBindings.length > 0) {
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

// ----------------------------------------------------
// Graph
// ----------------------------------------------------

function renderGraph(data) {
  destroyGraph();

  if (!data || !data.nodes || data.nodes.length === 0) {
    document.getElementById("graph").innerHTML =
      "<div style='padding:40px;text-align:center'>No relationship graph available.</div>";

    return;
  }

  graph = cytoscape({
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

          "text-wrap": "wrap",

          "text-max-width": 120,

          color: "#ffffff",

          "font-size": 12,

          "font-weight": "bold",

          width: 60,

          height: 60,

          "background-color": "#2563eb",

          "border-width": 2,

          "border-color": "#ffffff",
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
          shape: "round-rectangle",

          "background-color": "#0891b2",
        },
      },

      {
        selector: 'node[type="ClusterRoleBinding"]',

        style: {
          shape: "round-rectangle",

          "background-color": "#be185d",
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

      spacingFactor: 1.7,

      animate: true,
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

  html += "<p><b>Role Type:</b> " + item.kind + "</p>";

  html += "</div>";

  if (item.permissions && item.permissions.length > 0) {
    html += "<div class='card'>";

    html += "<h3>Permissions</h3>";

    item.permissions.forEach((rule) => {
      html += "<div class='permission'>";

      html += "<h4>" + ((rule.resources || []).join(", ") || "*") + "</h4>";

      html +=
        "<p><b>API Groups:</b> " +
        ((rule.apiGroups || []).join(", ") || "-") +
        "</p>";

      html += "<p><b>Verbs:</b> " + (rule.verbs || []).join(", ") + "</p>";

      html += "</div>";
    });

    html += "</div>";
  }

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

  if (item.permissions && item.permissions.length > 0) {
    html += "<div class='card'>";

    html += "<h3>Permissions</h3>";

    item.permissions.forEach((rule) => {
      html += "<div class='permission'>";

      html += "<h4>" + ((rule.resources || []).join(", ") || "*") + "</h4>";

      html +=
        "<p><b>API Groups:</b> " +
        ((rule.apiGroups || []).join(", ") || "-") +
        "</p>";

      html += "<p><b>Verbs:</b> " + (rule.verbs || []).join(", ") + "</p>";

      html += "</div>";
    });

    html += "</div>";
  }

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
