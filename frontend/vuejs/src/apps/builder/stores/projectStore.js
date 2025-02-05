import { defineStore } from 'pinia'
import axios from 'axios'

// Update API base URL to match Django's URL configuration
const API_BASE_URL = '/api/projectmanager/api'

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    loading: false,
    error: null,
    currentProject: null,
    initialized: false
  }),

  getters: {
    activeProjects: (state) => {
      // Return only active projects, ensuring no duplicates
      return state.projects.filter(p => p.is_active)
    },
    getProjectById: (state) => (id) => state.projects.find(p => p.id === id),
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    hasError: (state) => !!state.error,
    sortedProjects: (state) => {
      return [...state.projects].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    }
  },

  actions: {
    async fetchProjects() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE_URL}/projects/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        if (Array.isArray(response.data)) {
          // Create a Map to deduplicate projects by ID
          const uniqueProjects = new Map()
          response.data.forEach(project => {
            uniqueProjects.set(project.id, project)
          })
          this.projects = Array.from(uniqueProjects.values())
        } else {
          this.projects = []
        }
        
        this.initialized = true
        return this.projects
      } catch (err) {
        console.error('Failed to fetch projects:', err)
        if (err.response?.status === 404) {
          this.error = 'Unable to connect to project service. Please try again later.'
        } else if (err.response?.status === 401) {
          this.error = 'Please log in to view your projects.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to fetch projects'
        }
        this.projects = []
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchProject(projectId) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        this.currentProject = response.data
        return response.data
      } catch (err) {
        console.error('Failed to fetch project:', err)
        if (err.response?.status === 404) {
          this.error = 'Project not found.'
        } else if (err.response?.status === 401) {
          this.error = 'Please log in to view this project.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to fetch project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async createProject(projectData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE_URL}/projects/`, {
          name: projectData.name,
          description: projectData.description || `Web application project: ${projectData.name}`
        }, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        const newProject = response.data
        if (!newProject || typeof newProject.id === 'undefined') {
          throw new Error('Invalid project data received from server')
        }

        // Remove any existing projects with the same name before adding the new one
        this.projects = this.projects.filter(p => !(p.name === newProject.name && p.is_active))
        this.projects.unshift(newProject)
        
        // Refresh projects list to ensure consistency
        await this.fetchProjects()
        
        return newProject
      } catch (err) {
        console.error('Failed to create project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to create a project.'
        } else if (err.response?.status === 400) {
          this.error = err.response.data?.error || 'Invalid project data. Please try again.'
        } else if (err.response?.status === 500) {
          this.error = 'Server error while creating project. The project might have been created but had issues. Please check your projects list.'
        } else {
          this.error = err.message || 'Failed to create project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async updateProject({ projectId, projectData }) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.patch(`${API_BASE_URL}/projects/${projectId}/`, projectData, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        const updatedProject = response.data
        const index = this.projects.findIndex(p => p.id === projectId)
        if (index !== -1) {
          this.projects.splice(index, 1, updatedProject)
        }
        if (this.currentProject?.id === projectId) {
          this.currentProject = updatedProject
        }
        return updatedProject
      } catch (err) {
        console.error('Failed to update project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to update this project.'
        } else if (err.response?.status === 404) {
          this.error = 'Project not found.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to update project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteProject(projectId) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(`${API_BASE_URL}/projects/${projectId}/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json'
          }
        })
        this.projects = this.projects.filter(p => p.id !== projectId)
        if (this.currentProject?.id === projectId) {
          this.currentProject = null
        }
      } catch (err) {
        console.error('Failed to delete project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to delete projects.'
        } else if (err.response?.status === 404) {
          this.error = 'Project not found.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to delete project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    setCurrentProject(project) {
      this.currentProject = project
    },

    clearError() {
      this.error = null
    }
  }
}) 