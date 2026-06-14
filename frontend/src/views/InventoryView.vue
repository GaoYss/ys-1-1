<template>
  <section>
    <PageHeader eyebrow="Inventory" title="原料库存预警">
      <button class="primary-btn" @click="submitIngredient">
        {{ editingId ? '保存修改' : '保存原料' }}
      </button>
      <button v-if="editingId" class="secondary-btn" @click="resetForm">取消编辑</button>
    </PageHeader>

    <section class="form-panel">
      <div v-if="formError" class="error-text">{{ formError }}</div>
      <div class="form-grid">
        <label>
          原料名称
          <input v-model="form.name" placeholder="如：椰果" />
        </label>
        <label>
          分类
          <input v-model="form.category" placeholder="茶叶 / 小料 / 乳制品" />
        </label>
        <label>
          单位
          <input v-model="form.unit" placeholder="kg / L / 瓶" />
        </label>
        <label>
          当前库存
          <input v-model.number="form.stock" type="number" min="0" />
        </label>
        <label>
          关注阈值
          <input v-model.number="form.warningThreshold" type="number" min="0" />
        </label>
        <label>
          紧急阈值
          <input v-model.number="form.urgentThreshold" type="number" min="0" />
        </label>
        <label>
          默认供应商
          <select v-model.number="form.supplierId">
            <option :value="null">未指定</option>
            <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
              {{ supplier.name }}
            </option>
          </select>
        </label>
      </div>
    </section>

    <div class="toolbar">
      <input v-model="keyword" placeholder="搜索原料" @input="loadInventory" />
      <select v-model="warningFilter" @change="loadInventory">
        <option value="">全部状态</option>
        <option value="attention">关注</option>
        <option value="urgent">紧急</option>
        <option value="out_of_stock">断货</option>
        <option value="normal">正常</option>
      </select>
    </div>

    <DataTable :columns="columns" :rows="inventory">
      <template #stock="{ row }">{{ row.stock }} {{ row.unit }}</template>
      <template #warningThreshold="{ row }">{{ row.warningThreshold }} {{ row.unit }}</template>
      <template #urgentThreshold="{ row }">{{ row.urgentThreshold }} {{ row.unit }}</template>
      <template #warning="{ row }">
        <StatusBadge
          :label="warningLevelText(row.warningLevel)"
          :variant="warningLevelVariant(row.warningLevel)"
        />
      </template>
      <template #actions="{ row }">
        <button class="secondary-btn" @click="startEdit(row)">编辑</button>
      </template>
    </DataTable>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { inventoryApi } from '../api/inventory'
import DataTable from '../components/DataTable.vue'
import PageHeader from '../components/PageHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { warningLevelText, warningLevelVariant } from '../utils/format'

const route = useRoute()

const inventory = ref([])
const suppliers = ref([])
const keyword = ref('')
const warningFilter = ref('')
const editingId = ref(null)
const formError = ref('')
const form = reactive({
  name: '',
  category: '',
  unit: '',
  stock: 0,
  warningThreshold: 0,
  urgentThreshold: 0,
  supplierId: null
})

const columns = [
  { key: 'name', label: '原料' },
  { key: 'category', label: '分类' },
  { key: 'stock', label: '库存' },
  { key: 'warningThreshold', label: '关注阈值' },
  { key: 'urgentThreshold', label: '紧急阈值' },
  { key: 'supplierName', label: '供应商' },
  { key: 'warning', label: '状态' },
  { key: 'actions', label: '操作' }
]

function validateForm() {
  if (form.stock < 0) {
    formError.value = '当前库存必须大于等于零，请检查后再提交'
    return false
  }
  if (form.warningThreshold < 0) {
    formError.value = '关注阈值必须大于等于零，请检查后再提交'
    return false
  }
  if (form.urgentThreshold < 0) {
    formError.value = '紧急阈值必须大于等于零，请检查后再提交'
    return false
  }
  if (form.urgentThreshold > form.warningThreshold) {
    formError.value = '紧急阈值不能大于关注阈值，请检查后再提交'
    return false
  }
  formError.value = ''
  return true
}

async function loadInventory() {
  const params = {
    keyword: keyword.value || undefined
  }
  if (warningFilter.value) {
    params.warningLevel = warningFilter.value
  }
  const res = await inventoryApi.list(params)
  inventory.value = res.data
}

async function loadOptions() {
  const res = await inventoryApi.options()
  suppliers.value = res.data.suppliers
}

function resetForm() {
  editingId.value = null
  formError.value = ''
  Object.assign(form, {
    name: '',
    category: '',
    unit: '',
    stock: 0,
    warningThreshold: 0,
    urgentThreshold: 0,
    supplierId: null
  })
}

function startEdit(row) {
  editingId.value = row.id
  formError.value = ''
  Object.assign(form, {
    name: row.name,
    category: row.category,
    unit: row.unit,
    stock: row.stock,
    warningThreshold: row.warningThreshold,
    urgentThreshold: row.urgentThreshold,
    supplierId: row.supplierId
  })
}

async function submitIngredient() {
  if (!validateForm()) return
  try {
    if (editingId.value) {
      await inventoryApi.update(editingId.value, { ...form })
    } else {
      await inventoryApi.create({ ...form })
    }
    resetForm()
    await loadInventory()
  } catch (err) {
    if (err.response && err.response.data && err.response.data.error) {
      formError.value = err.response.data.error
    } else {
      formError.value = '保存失败，请稍后重试'
    }
  }
}

onMounted(async () => {
  await Promise.all([loadInventory(), loadOptions()])
})

watch(
  () => route.fullPath,
  async () => {
    if (route.path === '/inventory') {
      await Promise.all([loadInventory(), loadOptions()])
    }
  }
)
</script>
