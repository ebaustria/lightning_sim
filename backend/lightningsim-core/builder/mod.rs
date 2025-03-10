mod axi_builder;
mod axi_rctl;
mod edge_builder;
mod event;
mod fifo_builder;
mod frame;
mod module_builder;
mod node;
mod tee;

use std::{collections::hash_map::Entry, mem, sync::Arc};

use axi_builder::{
    AxiBuilder, AxiRequestRange, InsertedAxiRead, InsertedAxiReadReq, InsertedAxiWrite,
    InsertedAxiWriteReq, InsertedAxiWriteResp,
};
use edge_builder::{EdgeBuilder, IncompleteEdgeType};
use event::Event;
use fifo_builder::{FifoBuilder, InsertedFifoRead, InsertedFifoWrite};
use frame::StackFrame;
use module_builder::ModuleBuilder;
use node::{NodeTime, UncommittedNode};

use pyo3::{exceptions::PyValueError, prelude::*};
use rustc_hash::FxHashMap;

use crate::{
    axi_interface::{AxiAddress, AxiInterface, AxiInterfaceIoNodes},
    edge::Edge,
    fifo::{Fifo, FifoId, FifoIoNodes},
    node::{NodeIndex, NodeWithDelay},
    ClockCycle, CompiledSimulation, SimulationStage,
};

use self::axi_builder::FirstReadData;

#[pyclass]
#[derive(Clone)]
pub struct SimulationBuilder {
    builders: SimulationComponentBuilders,
    stack: Vec<StackFrame>,
}

#[derive(Clone)]
struct SimulationComponentBuilders {
    edges: EdgeBuilder,
    modules: ModuleBuilder,
    fifos: FxHashMap<Fifo, FifoBuilder>,
    axi: FxHashMap<AxiInterface, AxiBuilder>,
    end_node: Option<NodeIndex>,
}

#[pymethods]
impl SimulationBuilder {
    #[new]
    pub fn new() -> Self {
        let mut edges = EdgeBuilder::new();
        let start_node = edges.insert_node();
        let mut modules = ModuleBuilder::new();
        let top_module_key = modules.insert_module(None, 0, true);
        let top_module_start_edge = edges.insert_edge(IncompleteEdgeType::ControlFlow);
        edges.update_source(
            top_module_start_edge,
            NodeWithDelay {
                node: start_node,
                delay: 0,
            },
        );
        let top_frame = StackFrame::new(top_module_key, 0, top_module_start_edge);
        SimulationBuilder {
            builders: SimulationComponentBuilders {
                edges,
                modules,
                fifos: FxHashMap::default(),
                axi: FxHashMap::default(),
                end_node: None,
            },
            stack: vec![top_frame],
        }
    }

    pub fn add_fifo_write(
        &mut self,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        fifo_id: FifoId,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let fifo = Fifo { id: fifo_id };
            self.builders
                .add_fifo_write(frame, safe_offset, stage, fifo);
        }
    }

    pub fn add_fifo_read(
        &mut self,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        fifo_id: FifoId,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let fifo = Fifo { id: fifo_id };
            self.builders.add_fifo_read(frame, safe_offset, stage, fifo);
        }
    }

    pub fn add_axi_readreq(
        &mut self,
        mod_id: u8,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface_address: AxiAddress,
        request: AxiRequestRange,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let interface = AxiInterface {
                address: interface_address,
            };
            self.builders
                .add_axi_readreq(mod_id, frame, safe_offset, stage, interface, &request);
        }
    }

    pub fn add_axi_writereq(
        &mut self,
        mod_id: u8,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface_address: AxiAddress,
        request: AxiRequestRange,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let interface = AxiInterface {
                address: interface_address,
            };
            self.builders
                .add_axi_writereq(mod_id, frame, safe_offset, stage, interface, &request);
        }
    }

    pub fn add_axi_read(
        &mut self,
        mod_id: u8,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface_address: AxiAddress,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let interface = AxiInterface {
                address: interface_address,
            };
            self.builders
                .add_axi_read(mod_id, frame, safe_offset, stage, interface);
        }
    }

    pub fn add_axi_write(
        &mut self,
        mod_id: u8,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface_address: AxiAddress,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let interface = AxiInterface {
                address: interface_address,
            };
            self.builders
                .add_axi_write(mod_id, frame, safe_offset, stage, interface);
        }
    }

    pub fn add_axi_writeresp(
        &mut self,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface_address: AxiAddress,
    ) {
        if let Some(frame) = self.stack.last_mut() {
            let interface = AxiInterface {
                address: interface_address,
            };
            self.builders
                .add_axi_writeresp(frame, safe_offset, stage, interface);
        }
    }

    pub fn call(
        &mut self,
        safe_offset: SimulationStage,
        start_stage: SimulationStage,
        end_stage: SimulationStage,
        start_delay: ClockCycle,
        inherit_ap_continue: bool,
    ) {
        if let Some(parent) = self.stack.last_mut() {
            let frame = self.builders.call(
                parent,
                safe_offset,
                start_stage,
                end_stage,
                start_delay,
                inherit_ap_continue,
            );
            self.stack.push(frame);
        }
    }

    pub fn return_(&mut self, module_name: String, end_stage: SimulationStage) {
        if let Some(frame) = self.stack.pop() {
            let parent = self.stack.last_mut();
            self.builders.return_(frame, parent, module_name, end_stage);
        }
    }

    pub fn finish(&mut self) -> PyResult<CompiledSimulation> {
        mem::take(self).try_into()
    }
}

impl Default for SimulationBuilder {
    fn default() -> Self {
        Self::new()
    }
}

impl SimulationComponentBuilders {
    fn add_fifo_write(
        &mut self,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        fifo: Fifo,
    ) {
        let InsertedFifoWrite { index, raw_edge } =
            self.fifos.entry(fifo).or_default().insert_write();
        let raw_edge = raw_edge.unwrap_or_else(|err| {
            let new_edge = self.edges.insert_edge(IncompleteEdgeType::FifoRaw(fifo));
            err.provide_next(new_edge);
            new_edge
        });
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::FifoWrite {
                fifo,
                index,
                raw_edge,
            },
        );
    }

    fn add_fifo_read(
        &mut self,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        fifo: Fifo,
    ) {
        let InsertedFifoRead { index, raw_edge } =
            self.fifos.entry(fifo).or_default().insert_read();
        let raw_edge = raw_edge.unwrap_or_else(|err| {
            let new_edge = self.edges.insert_edge(IncompleteEdgeType::FifoRaw(fifo));
            err.provide_next(new_edge);
            new_edge
        });
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::FifoRead {
                fifo,
                index,
                raw_edge,
            },
        );
    }

    fn add_axi_readreq(
        &mut self,
        mod_id: u8,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface: AxiInterface,
        request: &AxiRequestRange,
    ) {
        let builder = self.axi.entry(interface).or_default();
        let read_edge = self
            .edges
            .insert_edge(IncompleteEdgeType::AxiRead(interface));
        let rctl_in_edge = self
            .edges
            .insert_edge(IncompleteEdgeType::AxiRctl(interface));
        let rctl_out_edge = self
            .edges
            .insert_edge(IncompleteEdgeType::AxiRctl(interface));
        let InsertedAxiReadReq { index, rctl_txn } =
            builder.insert_readreq(request, read_edge, rctl_in_edge, rctl_out_edge);
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::AxiReadRequest {
                mod_id,
                interface,
                index,
                read_edge,
                rctl_txn,
            },
        );
    }

    fn add_axi_writereq(
        &mut self,
        mod_id: u8,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface: AxiInterface,
        request: &AxiRequestRange,
    ) {
        let InsertedAxiWriteReq { index } = self
            .axi
            .entry(interface)
            .or_default()
            .insert_writereq(request);
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::AxiWriteRequest { mod_id, interface, index },
        );
    }

    fn add_axi_read(
        &mut self,
        mod_id: u8,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface: AxiInterface,
    ) {
        let InsertedAxiRead {
            index,
            first_read,
            rctl_out_edge,
        } = self.axi.entry(interface).or_default().insert_read();
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::AxiRead {
                mod_id,
                interface,
                index,
                first_read,
                rctl_out_edge,
            },
        );
    }

    fn add_axi_write(
        &mut self,
        mod_id: u8,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface: AxiInterface,
    ) {
        let InsertedAxiWrite {
            index,
            writeresp_edge,
        } = self.axi.entry(interface).or_default().insert_write();
        let writeresp_edge = writeresp_edge.map(|edge_needed| {
            let new_edge = self
                .edges
                .insert_edge(IncompleteEdgeType::AxiWriteResp(interface));
            edge_needed.provide(new_edge);
            new_edge
        });
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::AxiWrite {
                mod_id,
                interface,
                index,
                writeresp_edge,
            },
        );
    }

    fn add_axi_writeresp(
        &mut self,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        interface: AxiInterface,
    ) {
        let InsertedAxiWriteResp {
            index,
            writeresp_edge,
        } = self.axi.entry(interface).or_default().insert_writeresp();
        self.add_event(
            frame,
            safe_offset,
            stage,
            Event::AxiWriteResponse {
                interface,
                index,
                writeresp_edge,
            },
        );
    }

    #[must_use]
    fn call(
        &mut self,
        parent: &mut StackFrame,
        safe_offset: SimulationStage,
        start_stage: SimulationStage,
        end_stage: SimulationStage,
        start_delay: ClockCycle,
        inherit_ap_continue: bool,
    ) -> StackFrame {
        let start_edge = self.edges.insert_edge(IncompleteEdgeType::ControlFlow);
        self.edges.add_delay(start_edge, start_delay);
        let module_key =
            self.modules
                .insert_module(Some(parent.key), start_delay, inherit_ap_continue);
        self.add_event(
            parent,
            safe_offset,
            start_stage,
            Event::SubcallStart {
                module_key,
                edge: start_edge,
            },
        );
        StackFrame::new(module_key, end_stage, start_edge)
    }

    fn return_(
        &mut self,
        mut frame: StackFrame,
        parent: Option<&mut StackFrame>,
        module_name: String,
        end_stage: SimulationStage,
    ) {
        while let Some(uncommitted_node) = frame.window.pop_front() {
            let advance_by = SimulationStage::from(!frame.window.is_empty());
            self.commit_node(&mut frame, uncommitted_node, advance_by);
        }
        if let Some(remaining_stages) = end_stage.checked_sub(frame.offset) {
            let remaining_delay = remaining_stages.into();
            frame.current_time += remaining_delay;
            self.edges.add_delay(frame.current_edge, remaining_delay);
        }

        self.modules.update_module_name(frame.key, module_name);
        self.modules
            .update_module_end(frame.key, frame.current_time);

        if let Some(parent) = parent {
            parent.add_event(
                frame.parent_end,
                Event::SubcallEnd {
                    edge: frame.current_edge,
                },
            );
        } else {
            for axi_rctl in mem::take(self.modules.get_axi_rctl_mut(frame.key)).into_values() {
                axi_rctl.finish(&mut self.edges);
            }
            let deferred = self
                .modules
                .commit_module(frame.key, NodeWithDelay { node: 0, delay: 0 });
            for (node, event) in deferred {
                debug_assert!(!event.has_in_edge());
                self.commit_event(event, node);
            }
            self.end_node = Some(self.edges.insert_node());
            self.edges.push_destination(frame.current_edge);
        }
    }

    fn finalize_event(&mut self, frame: &mut StackFrame, event: &Event) {
        match *event {
            Event::AxiReadRequest {
                interface,
                rctl_txn,
                ..
            } => {
                self.modules
                    .get_axi_rctl_mut(frame.key)
                    .entry(interface)
                    .or_default()
                    .push(&mut self.edges, rctl_txn);
            }
            Event::SubcallStart { module_key, .. } => {
                for (interface, sub_axi_rctl) in
                    mem::take(self.modules.get_axi_rctl_mut(module_key))
                {
                    match self.modules.get_axi_rctl_mut(frame.key).entry(interface) {
                        Entry::Occupied(mut entry) => {
                            entry.get_mut().extend(&mut self.edges, sub_axi_rctl);
                        }
                        Entry::Vacant(entry) => {
                            entry.insert(sub_axi_rctl);
                        }
                    }
                }
            }
            _ => {}
        }
    }

    fn commit_event(&mut self, event: Event, node: NodeWithDelay) {
        match event {
            Event::SubcallStart { module_key, edge } => {
                let deferred = self.modules.commit_module(module_key, node);
                self.edges.update_source(edge, node);
                for (node, event) in deferred {
                    debug_assert!(!event.has_in_edge());
                    self.commit_event(event, node);
                }
            }
            Event::SubcallEnd { edge } => {
                self.edges.push_destination(edge);
            }
            Event::FifoRead {
                fifo,
                index,
                raw_edge,
            } => {
                self.fifos.get_mut(&fifo).unwrap().update_read(index, node);
                self.edges.push_destination(raw_edge);
            }
            Event::FifoWrite {
                fifo,
                index,
                raw_edge,
            } => {
                self.fifos.get_mut(&fifo).unwrap().update_write(index, node);
                self.edges.update_source(raw_edge, node);
                if index != 0 {
                    self.edges.push_edge(Edge::FifoWar { fifo, index });
                }
            }
            Event::AxiReadRequest {
                mod_id,
                interface,
                index,
                read_edge,
                rctl_txn: _,
            } => {
                self.axi
                    .get_mut(&interface)
                    .unwrap()
                    .update_readreq(index, node, mod_id);
                self.edges.update_source(read_edge, node);
            }
            Event::AxiRead {
                mod_id,
                interface,
                index,
                first_read,
                rctl_out_edge,
            } => {
                let axi_builder = self.axi.get_mut(&interface).unwrap();
                axi_builder.update_read(index, node, mod_id);
                if let Some(rctl_out_edge) = rctl_out_edge {
                    self.edges.update_source(rctl_out_edge, node);
                }
                if let Some(FirstReadData {
                    read_edge,
                    rctl_in_edge,
                }) = first_read
                {
                    self.edges.push_destination(read_edge);
                    self.edges.push_destination(rctl_in_edge);
                }
            }
            Event::AxiWriteRequest { mod_id, interface, index } => {
                self.axi
                    .get_mut(&interface)
                    .unwrap()
                    .update_writereq(index, node, mod_id);
            }
            Event::AxiWrite {
                mod_id,
                interface,
                index,
                writeresp_edge,
            } => {
                self.axi
                    .get_mut(&interface)
                    .unwrap()
                    .update_write(index, node, mod_id);
                if let Some(writeresp_edge) = writeresp_edge {
                    self.edges.update_source(writeresp_edge, node);
                }
            }
            Event::AxiWriteResponse {
                interface,
                index,
                writeresp_edge,
            } => {
                self.axi
                    .get_mut(&interface)
                    .unwrap()
                    .update_writeresp(index, node);
                self.edges.push_destination(writeresp_edge);
            }
        }
    }

    fn commit_node(
        &mut self,
        frame: &mut StackFrame,
        uncommitted_node: UncommittedNode,
        advance_by: SimulationStage,
    ) {
        frame.offset += advance_by;
        let delay = advance_by.into();
        let unstalled_time = frame.current_time;
        let stalled_time = if uncommitted_node.is_own_node() {
            let node = self.edges.insert_node();
            self.edges.push_destination(frame.current_edge);
            let node_with_delay = NodeWithDelay { node, delay };
            frame.current_edge = self.edges.insert_edge(IncompleteEdgeType::ControlFlow);
            frame.current_time = NodeTime::Absolute(node_with_delay);
            self.edges
                .update_source(frame.current_edge, node_with_delay);
            NodeTime::Absolute(NodeWithDelay { node, delay: 0 })
        } else {
            self.edges.add_delay(frame.current_edge, delay);
            frame.current_time += delay;
            unstalled_time
        };
        for event in uncommitted_node.events {
            let event_time = if event.is_stalled() {
                stalled_time
            } else {
                unstalled_time
            };
            self.finalize_event(frame, &event);
            match event_time {
                NodeTime::Absolute(node) => self.commit_event(event, node),
                NodeTime::RelativeToStart(delay) => {
                    self.modules.defer_event(frame.key, delay, event);
                }
            }
        }
    }

    fn commit_until(&mut self, frame: &mut StackFrame, stage: SimulationStage) {
        while frame.offset < stage {
            match frame.window.pop_front() {
                Some(uncommitted_node) => self.commit_node(frame, uncommitted_node, 1),
                None => break,
            };
        }
        if let Some(remaining_stages) = stage.checked_sub(frame.offset) {
            let remaining_delay = remaining_stages.into();
            frame.offset = stage;
            frame.current_time += remaining_delay;
            self.edges.add_delay(frame.current_edge, remaining_delay);
        }
    }

    fn add_event(
        &mut self,
        frame: &mut StackFrame,
        safe_offset: SimulationStage,
        stage: SimulationStage,
        event: Event,
    ) {
        self.commit_until(frame, safe_offset);
        frame.add_event(stage, event);
    }
}

impl TryFrom<SimulationBuilder> for CompiledSimulation {
    type Error = PyErr;

    fn try_from(value: SimulationBuilder) -> Result<Self, Self::Error> {
        value.builders.try_into()
    }
}

impl TryFrom<SimulationComponentBuilders> for CompiledSimulation {
    type Error = PyErr;

    fn try_from(value: SimulationComponentBuilders) -> Result<Self, Self::Error> {
        Ok(CompiledSimulation {
            graph: value.edges.try_into()?,
            top_module: value.modules.try_into()?,
            fifo_nodes: Arc::new(value
                .fifos
                .into_iter()
                .map(|(fifo, builder)| builder.try_into().map(|nodes: FifoIoNodes| (fifo, nodes)))
                .collect::<Result<_, _>>()?),
            axi_interface_nodes: Arc::new(value
                .axi
                .into_iter()
                .map(|(axi_interface, builder)| {
                    builder
                        .try_into()
                        .map(|nodes: AxiInterfaceIoNodes| (axi_interface, nodes))
                })
                .collect::<Result<_, _>>()?),
            end_node: value
                .end_node
                .ok_or_else(|| PyValueError::new_err("incomplete trace"))?,
        })
    }
}
