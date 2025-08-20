async function renderModelCardsDashboard() {
  const response = await fetch('/api/models');
  if (!response.ok) throw new Error('Failed to fetch models');
  const models = await response.json();

  const dashboard = document.getElementById('model-cards-dashboard');
  dashboard.innerHTML = '';

  Object.entries(models).forEach(([modelName, modelData]) => {
    const card = document.createElement('div');
    card.className = 'model-card';
    card.innerHTML = `
      <h3><a href="/admin/dashboard/${modelName}">${modelName}</a> - ${modelData} entities</h3>
    `;
    dashboard.appendChild(card);
  });
}

async function renderModelTableDashboard() {
  const response = await fetch(`/api/model/${location.pathname.split('/').pop(-1)}`);
  if (!response.ok) throw new Error('Failed to fetch model data');
  const modelData = await response.json();

  const dashboard = document.getElementById('model-table-dashboard');
  dashboard.innerHTML = '';

  const header = document.createElement('p');
  header.className = 'model-header';
  Object.entries(modelData[0]).forEach(([key, value]) => {
    header.innerHTML += ` <strong>${key}</strong> `;
  });
  dashboard.appendChild(header);

  modelData.forEach(item => {
    const modelRow = document.createElement('p');
    modelRow.className = 'model-row';
    Object.entries(item).forEach(([key, value]) => {
      if (typeof(value) === 'object' && value !== null) {
        if ((value?.id?.toString() ?? 'NONE') === 'NONE') {
          modelRow.innerHTML += ` ${key.toUpperCase()}.NONE `;
        } else {
          modelRow.innerHTML += ` <a href="/admin/dashboard/${key}/${value.id.toString()}">${key.toUpperCase()}.${value.id.toString()}</a> `;
        }
      } else {
        modelRow.innerHTML += ` ${value} `;
      }
    });
    dashboard.appendChild(modelRow);
  });
}

async function renderModelInstanceDashboard() {
  const response = await fetch(`/api/model/${location.pathname.split('/').slice(-2, -1)}/${location.pathname.split('/').pop(-1)}`);
  if (!response.ok) throw new Error('Failed to fetch model instance data');
  const modelInstanceData = await response.json();

  const dashboard = document.getElementById('model-instance-dashboard');
  dashboard.innerHTML = '';

  const header = document.createElement('p');
  header.className = 'model-header';
  Object.entries(modelInstanceData).forEach(([key, value]) => {
    header.innerHTML += ` <strong>${key}</strong> `;
  });
  dashboard.appendChild(header);

  const modelRow = document.createElement('p');
  modelRow.className = 'model-row';
  Object.entries(modelInstanceData).forEach(([key, value]) => {
    if (typeof(value) === 'object' && value !== null) {
      if ((value?.id?.toString() ?? 'NONE') === 'NONE') {
        modelRow.innerHTML += ` ${key.toUpperCase()}.NONE `;
      } else {
        modelRow.innerHTML += ` <a href="/admin/dashboard/${key}/${value.id.toString()}">${key.toUpperCase()}.${value.id.toString()}</a> `;
      }
    } else {
      modelRow.innerHTML += ` ${value} `;
    }
  });
  dashboard.appendChild(modelRow);
}

document.addEventListener('DOMContentLoaded', () => {
  if (location.pathname === '/admin/dashboard') {
    renderModelCardsDashboard();
  } else if (location.pathname.startsWith('/admin/dashboard/') && location.pathname.split('/').length === 4) {
    renderModelTableDashboard();
  } else if (location.pathname.startsWith('/admin/dashboard/') && location.pathname.split('/').length === 5) {
    renderModelInstanceDashboard();
  }
});