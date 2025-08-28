#!/usr/bin/env python3
import os
import re

# Define the template structure for each entity
entities = {
    'partners': {
        'title': 'إضافة شريك جديد',
        'button_color': 'orange',
        'table_id': 'partner-table-body'
    },
    'safes': {
        'title': 'إضافة خزنة جديدة',
        'button_color': 'indigo',
        'table_id': 'safe-table-body'
    },
    'units': {
        'title': 'إضافة وحدة جديدة',
        'button_color': 'teal',
        'table_id': 'unit-table-body'
    },
    'store': {
        'title': 'إضافة صنف جديد',
        'button_color': 'yellow',
        'table_id': 'item-table-body'
    }
}

# Template for list page with modal
list_template = """{% extends "base.html" %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-gray-800">{{ page_title }}</h1>
    <button 
        onclick="showAddForm()"
        class="bg-{color}-600 hover:bg-{color}-700 text-white font-bold py-2 px-6 rounded-lg shadow-md transition duration-300 flex items-center">
        <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        {title}
    </button>
</div>

<!-- Modal Container -->
<div id="form-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 hidden">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div class="flex justify-between items-center pb-3 border-b">
            <h3 class="text-xl font-bold text-gray-900">{title}</h3>
            <button onclick="closeFormModal()" class="text-gray-400 hover:text-gray-600">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="mt-4" id="form-container">
            {% include '{include_path}' with form=form %}
        </div>
    </div>
</div>

{table_content}

<script>
function showAddForm() {
    document.getElementById('form-modal').classList.remove('hidden');
}

function closeFormModal() {
    document.getElementById('form-modal').classList.add('hidden');
    // Reset form if needed
    document.querySelector('#form-container form').reset();
}

// Close modal when clicking outside
window.onclick = function(event) {
    let modal = document.getElementById('form-modal');
    if (event.target == modal) {
        closeFormModal();
    }
}

// Handle successful form submission
document.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === '{table_id}') {
        closeFormModal();
    }
});
</script>
{% endblock %}"""

print("Script to update templates created. Run it manually to update all templates.")