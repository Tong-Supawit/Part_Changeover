<template>
  <v-app>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card class="pa-4 elevation-3">
            <v-card-title class="headline text-center">Master Parts Changeover Matrix</v-card-title>

            <v-simple-table class="mb-4 custom-table">
              <thead>
                <tr>
                  <th>Part No</th>
                  <th v-for="part in parts" :key="part">{{ part }}</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in matrix" :key="rowIndex">
                  <td>{{ parts[rowIndex] }}</td>
                  <td
                    v-for="(time, colIndex) in row"
                    :key="colIndex"
                    :class="{'highlighted': parts[rowIndex] === parts[colIndex]}"
                  >
                    <template v-if="parts[rowIndex] === parts[colIndex]">
                    </template>
                    <v-text-field
                      v-else
                      v-model="matrix[rowIndex][colIndex]"
                      @blur="updateTime(parts[rowIndex], parts[colIndex], matrix[rowIndex][colIndex])"
                      outlined
                      dense
                      type="number"
                      class="matrix-input"
                    ></v-text-field>
                  </td>
                  <td>
                    <v-btn color="red" small @click="deletePart(parts[rowIndex])">Delete</v-btn>
                  </td>
                </tr>
              </tbody>
            </v-simple-table>

            <v-text-field
              v-model="newPart"
              label="Enter Part No"
              outlined
              dense
              class="mt-4"
            ></v-text-field>
            
            <v-btn @click="addPart" color="primary" class="mt-2" outlined>
              Add Part
            </v-btn>
            <br>

            <v-btn @click="downloadExcel" color="success" class="mt-4" outlined>
              Download Excel
            </v-btn>
            <br>
            
            <v-btn color="pink" class="mt-4 upload-button" outlined @click="triggerFileInput">
              Upload Excel
            </v-btn>
            <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      parts: [],
      matrix: [],
      newPart: ''
    };
  },
  methods: {
    async downloadExcel() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/download", { responseType: "blob" });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "matrix_data.xlsx");
        document.body.appendChild(link);
        link.click();
      } catch (error) {
        console.error("Error downloading file:", error);
      }
    },

    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    async handleFileUpload(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        console.log(response.data.message);
        this.fetchMatrixData();
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    },

    async addPart() {
      try {
        const response = await axios.post("http://127.0.0.1:8000/add-part", { part_no: this.newPart });
        console.log(response.data.message);
        this.fetchMatrixData();
        this.newPart = '';
      } catch (error) {
        console.error("Error adding part:", error);
      }
    },

    async deletePart(partNo) {
      try {
        const response = await axios.delete("http://127.0.0.1:8000/delete-part", {
          params: { part_no: partNo }
        });
        console.log(response.data.message);
        this.fetchMatrixData();
      } catch (error) {
        console.error("Error deleting part:", error);
      }
    },

    async updateTime(partNo, targetPartNo, changeoverTime) {
      try {
        await axios.put("http://127.0.0.1:8000/update-time", {
          part_no: partNo,
          target_part_no: targetPartNo,
          changeover_time: changeoverTime
        });
        console.log(`Time updated for ${partNo} -> ${targetPartNo}`);
      } catch (error) {
        console.error("Error updating time:", error);
      }
    },

    async fetchMatrixData() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/matrix-data");
        this.parts = response.data.parts;
        this.matrix = response.data.matrix;
      } catch (error) {
        console.error("Error fetching matrix data:", error);
      }
    }
  },
  mounted() {
    this.fetchMatrixData();
  }
};
</script>

<style scoped>
  
.custom-table {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.custom-table thead th, .custom-table tbody td {
  border: 1px solid #000;
  padding: 0px;
  text-align: center;
  word-wrap: break-word;
  font-size: 0.85em;
  height: 50px;
}

.custom-table thead th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.custom-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.highlighted {
  background-color: #d3d3d3;
}

.matrix-input {
  width: 100%;
  text-align: center;
  padding: 0px;
  font-size: 0.85em;
  height: 55px;
}
</style>
